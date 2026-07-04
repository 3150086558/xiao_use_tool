from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.user import User
from ..models.menu import Menu
from ..models.record import Record
from ..models.todo import Todo
from ..models.note import Note
from ..models.db_connection import DbConnection
from ..models.refresh_token import RefreshToken
from ..schemas.user import UserAdminResponse, ResetPasswordRequest
from ..security import hash_password, validate_password
from ..deps import get_current_admin_user

router = APIRouter()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[UserAdminResponse])
def list_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(_get_db),
):
    users = db.query(User).order_by(User.id).all()
    result = []
    for user in users:
        record_count = db.query(Record).filter(Record.user_id == user.id).count()
        todo_count = db.query(Todo).filter(Todo.user_id == user.id).count()
        note_count = db.query(Note).filter(Note.user_id == user.id).count()
        resp = UserAdminResponse.model_validate(user)
        resp.record_count = record_count
        resp.todo_count = todo_count
        resp.note_count = note_count
        result.append(resp)
    return result


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(_get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.query(Record).filter(Record.user_id == user_id).delete()
    db.query(Todo).filter(Todo.user_id == user_id).delete()
    db.query(Note).filter(Note.user_id == user_id).delete()
    db.query(Menu).filter(Menu.user_id == user_id).delete()
    db.query(DbConnection).filter(DbConnection.user_id == user_id).delete()
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    return {"ok": True, "message": "用户已删除"}


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    data: ResetPasswordRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(_get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    valid, msg = validate_password(data.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    user.password = hash_password(data.new_password)
    db.commit()
    return {"ok": True, "message": "密码重置成功"}
