from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.user import User
from ..models.menu import Menu
from ..models.refresh_token import RefreshToken
from ..schemas.auth import (
    RegisterRequest, LoginRequest, LoginResponse,
    RefreshTokenRequest, ChangePasswordRequest, UserResponse
)
from ..security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, validate_password
from ..deps import get_current_user
from ..config import get_settings
from ..redis_client import get_redis
from .menus import init_default_menus

router = APIRouter()
settings = get_settings()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=LoginResponse)
def register(data: RegisterRequest, db: Session = Depends(_get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="两次密码输入不一致")
    valid, msg = validate_password(data.password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    is_first_user = db.query(User).count() == 0
    user = User(
        username=data.username,
        password=hash_password(data.password),
        is_admin=is_first_user,
    )
    db.add(user)
    db.flush()
    db.refresh(user)

    init_default_menus(db, user.id)

    access_token, access_expire = create_access_token(user.id)
    refresh_token, refresh_expire = create_refresh_token(user.id)

    db.add(RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_expire,
    ))
    db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user={"id": user.id, "username": user.username, "is_admin": user.is_admin},
    )


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(_get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    access_token, access_expire = create_access_token(user.id)
    refresh_token, refresh_expire = create_refresh_token(user.id)

    db.add(RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_expire,
    ))
    db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user={"id": user.id, "username": user.username, "is_admin": user.is_admin},
    )


@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    db.query(RefreshToken).filter(
        RefreshToken.token == refresh_data.refresh_token,
        RefreshToken.user_id == current_user.id,
    ).update({"revoked": True})
    db.commit()

    try:
        redis = get_redis()
        if redis:
            await redis.setex(
                f"blacklist:refresh:{refresh_data.refresh_token}",
                settings.refresh_token_expire_days * 86400,
                "1",
            )
    except Exception as e:
        pass

    return {"ok": True, "message": "已退出登录"}


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(_get_db),
):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    try:
        redis = get_redis()
        if redis:
            is_blacklisted = await redis.get(f"blacklist:refresh:{data.refresh_token}")
            if is_blacklisted:
                raise HTTPException(status_code=401, detail="令牌已注销")
    except Exception as e:
        pass

    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow(),
    ).first()
    if not token_record:
        raise HTTPException(status_code=401, detail="刷新令牌无效或已过期")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    access_token, access_expire = create_access_token(user.id)
    new_refresh_token, refresh_expire = create_refresh_token(user.id)

    token_record.revoked = True
    db.add(RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=refresh_expire,
    ))
    db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user={"id": user.id, "username": user.username, "is_admin": user.is_admin},
    )


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="原密码错误")
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的新密码不一致")
    valid, msg = validate_password(data.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    current_user.password = hash_password(data.new_password)
    db.commit()
    return {"ok": True, "message": "密码修改成功"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
