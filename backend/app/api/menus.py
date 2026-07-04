from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.user import User
from ..models.menu import Menu
from ..schemas.menu import MenuResponse
from ..deps import get_current_user

router = APIRouter()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_default_menus(db: Session, user_id: int):
    existing = db.query(Menu).filter(Menu.user_id == user_id).first()
    if existing:
        return

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    if user.is_admin:
        default_menus = [
            {"name": "财务管理", "icon": "Wallet", "sort_order": 1, "parent_name": None},
            {"name": "记账", "icon": "Notebook", "sort_order": 1, "parent_name": "财务管理"},
            {"name": "统计报表", "icon": "DataAnalysis", "sort_order": 2, "parent_name": "财务管理"},
            {"name": "日常工具", "icon": "Tools", "sort_order": 2, "parent_name": None},
            {"name": "待办事项", "icon": "List", "sort_order": 1, "parent_name": "日常工具"},
            {"name": "备忘录", "icon": "Document", "sort_order": 2, "parent_name": "日常工具"},
            {"name": "数据库查询", "icon": "Coin", "sort_order": 3, "parent_name": "日常工具"},
            {"name": "系统管理", "icon": "Setting", "sort_order": 3, "parent_name": None},
            {"name": "用户管理", "icon": "User", "sort_order": 1, "parent_name": "系统管理"},
        ]
    else:
        default_menus = [
            {"name": "财务管理", "icon": "Wallet", "sort_order": 1, "parent_name": None},
            {"name": "记账", "icon": "Notebook", "sort_order": 1, "parent_name": "财务管理"},
            {"name": "统计报表", "icon": "DataAnalysis", "sort_order": 2, "parent_name": "财务管理"},
            {"name": "日常工具", "icon": "Tools", "sort_order": 2, "parent_name": None},
            {"name": "待办事项", "icon": "List", "sort_order": 1, "parent_name": "日常工具"},
            {"name": "备忘录", "icon": "Document", "sort_order": 2, "parent_name": "日常工具"},
            {"name": "数据库查询", "icon": "Coin", "sort_order": 3, "parent_name": "日常工具"},
        ]

    menu_map = {}
    for menu_data in default_menus:
        parent_id = 0
        if menu_data.get("parent_name"):
            parent_id = menu_map.get(menu_data["parent_name"], 0)

        menu = Menu(
            user_id=user_id,
            parent_id=parent_id,
            name=menu_data["name"],
            icon=menu_data.get("icon", ""),
            sort_order=menu_data.get("sort_order", 0)
        )
        db.add(menu)
        db.flush()
        db.refresh(menu)
        menu_map[menu.name] = menu.id

    db.commit()


@router.get("", response_model=list[MenuResponse])
def get_menus(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    user_menus = db.query(Menu).filter(
        Menu.user_id == current_user.id
    ).order_by(Menu.sort_order, Menu.id).all()

    if not user_menus:
        init_default_menus(db, current_user.id)
        user_menus = db.query(Menu).filter(
            Menu.user_id == current_user.id
        ).order_by(Menu.sort_order, Menu.id).all()

    if not current_user.is_admin:
        user_menus = [m for m in user_menus if m.name != "系统管理"]

    def build_tree(parent_id: int = 0):
        children = [m for m in user_menus if m.parent_id == parent_id]
        result = []
        for menu in children:
            menu_dict = MenuResponse.model_validate(menu).model_dump()
            menu_dict["children"] = build_tree(menu.id)
            result.append(menu_dict)
        return result

    return build_tree(0)
