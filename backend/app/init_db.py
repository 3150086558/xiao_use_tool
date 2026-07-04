from sqlalchemy.orm import Session
from .database import engine, Base
from .models.user import User
from .models.menu import Menu
from .security import get_password_hash


def init_database():
    Base.metadata.create_all(bind=engine)
    
    db = Session(bind=engine)
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            hashed_password = get_password_hash("Admin@123")
            admin = User(
                username="admin",
                password=hashed_password,
                is_admin=True
            )
            db.add(admin)
            db.flush()
            db.refresh(admin)
            
            default_menus = [
                {"name": "首页", "icon": "HomeFilled", "sort_order": 0},
                {"name": "财务管理", "icon": "Wallet", "sort_order": 1},
                {"name": "记账", "icon": "Notebook", "sort_order": 2, "parent": "财务管理"},
                {"name": "统计报表", "icon": "DataAnalysis", "sort_order": 3, "parent": "财务管理"},
                {"name": "日常工具", "icon": "Tools", "sort_order": 4},
                {"name": "待办事项", "icon": "List", "sort_order": 5, "parent": "日常工具"},
                {"name": "备忘录", "icon": "Document", "sort_order": 6, "parent": "日常工具"},
                {"name": "数据库查询", "icon": "Coin", "sort_order": 7},
                {"name": "系统管理", "icon": "Setting", "sort_order": 8},
                {"name": "用户管理", "icon": "User", "sort_order": 9, "parent": "系统管理"},
            ]
            
            menu_map = {}
            for menu_data in default_menus:
                parent_id = 0
                if "parent" in menu_data:
                    parent_id = menu_map.get(menu_data["parent"], 0)
                
                menu = Menu(
                    user_id=admin.id,
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
            print("初始化数据库成功！")
            print("默认管理员账号: admin")
            print("默认管理员密码: Admin@123")
        else:
            print("数据库已初始化，跳过初始化步骤")
            
    except Exception as e:
        db.rollback()
        print(f"初始化数据库失败: {e}")
        raise
    finally:
        db.close()


def init_user_menus(user_id: int, db: Session):
    menus = db.query(Menu).filter(Menu.user_id == user_id).first()
    if menus:
        return
    
    default_menus = [
        {"name": "首页", "icon": "HomeFilled", "sort_order": 0},
        {"name": "财务管理", "icon": "Wallet", "sort_order": 1},
        {"name": "记账", "icon": "Notebook", "sort_order": 2, "parent": "财务管理"},
        {"name": "统计报表", "icon": "DataAnalysis", "sort_order": 3, "parent": "财务管理"},
        {"name": "日常工具", "icon": "Tools", "sort_order": 4},
        {"name": "待办事项", "icon": "List", "sort_order": 5, "parent": "日常工具"},
        {"name": "备忘录", "icon": "Document", "sort_order": 6, "parent": "日常工具"},
        {"name": "数据库查询", "icon": "Coin", "sort_order": 7},
    ]
    
    menu_map = {}
    for menu_data in default_menus:
        parent_id = 0
        if "parent" in menu_data:
            parent_id = menu_map.get(menu_data["parent"], 0)
        
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


if __name__ == "__main__":
    init_database()
