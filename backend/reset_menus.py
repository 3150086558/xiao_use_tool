import sys
sys.path.insert(0, '.')

from app.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.menu import Menu
from app.security import get_password_hash
from app.api.menus import init_default_menus


def reset_all_menus():
    db = SessionLocal()
    try:
        print("删除所有菜单数据...")
        db.query(Menu).delete()
        db.commit()

        print("重新为所有用户初始化菜单...")
        users = db.query(User).all()
        for user in users:
            print(f"  初始化用户 {user.username} 的菜单...")
            init_default_menus(db, user.id)

        print("菜单重置完成！")
    except Exception as e:
        db.rollback()
        print(f"重置失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def init_admin_user():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("创建默认管理员账号...")
            hashed_password = get_password_hash("Admin@123")
            admin = User(
                username="admin",
                password=hashed_password,
                is_admin=True
            )
            db.add(admin)
            db.flush()
            db.refresh(admin)
            print("创建管理员菜单...")
            init_default_menus(db, admin.id)
            db.commit()
            print("默认管理员账号创建成功！")
            print("账号: admin")
            print("密码: Admin@123")
        else:
            print("管理员账号已存在")
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    reset_all_menus()
    init_admin_user()
