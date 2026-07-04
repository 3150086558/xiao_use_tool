import sys
sys.path.insert(0, '.')

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.menu import Menu
from app.models.record import Record
from app.models.todo import Todo
from app.models.note import Note
from app.models.refresh_token import RefreshToken
from app.models.db_connection import DbConnection
from app.security import get_password_hash


def init_database():
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
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
                {"name": "首页", "icon": "HomeFilled", "sort_order": 0, "parent_name": None},
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
            
            menu_map = {}
            for menu_data in default_menus:
                parent_id = 0
                if menu_data.get("parent_name"):
                    parent_id = menu_map.get(menu_data["parent_name"], 0)
                
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
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
