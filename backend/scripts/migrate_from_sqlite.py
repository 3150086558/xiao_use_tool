#!/usr/bin/env python3
"""
从旧的 SQLite 数据库迁移数据到 PostgreSQL
用法：python scripts/migrate_from_sqlite.py [sqlite_path]
"""
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, engine
from app.models import User, Record, Menu, Todo, Note, DbConnection
from app.security import hash_password
from app.utils.crypto import encrypt_password
from sqlalchemy.orm import Session


def migrate_sqlite_to_pg(sqlite_path: str):
    print(f"正在从 {sqlite_path} 迁移数据到 PostgreSQL...")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    pg_db: Session = SessionLocal()

    try:
        users = sqlite_conn.execute("SELECT * FROM users").fetchall()
        user_id_map = {}

        admin_user = pg_db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("  创建 admin 用户（密码重置为 Mkld@2026）...")
            admin_user = User(
                username="admin",
                password=hash_password("Mkld@2026"),
                is_admin=True,
                created_at=datetime.utcnow(),
            )
            pg_db.add(admin_user)
            pg_db.flush()

        for u in users:
            username = u["username"]
            existing = pg_db.query(User).filter(User.username == username).first()
            if existing:
                user_id_map[u["id"]] = existing.id
                print(f"  用户 {username} 已存在，跳过")
                continue
            new_user = User(
                username=username,
                password=hash_password("Mkld@2026"),
                is_admin=(username == "admin"),
                created_at=datetime.strptime(u["created_at"], "%Y-%m-%d %H:%M:%S") if u["created_at"] else datetime.utcnow(),
            )
            pg_db.add(new_user)
            pg_db.flush()
            user_id_map[u["id"]] = new_user.id
            print(f"  创建用户: {username} (密码重置为 Mkld@2026)")

        pg_db.commit()
        print(f"用户迁移完成，共 {len(user_id_map)} 个用户")

        records = sqlite_conn.execute("SELECT * FROM records").fetchall()
        for r in records:
            new_user_id = user_id_map.get(r["user_id"])
            if not new_user_id:
                continue
            try:
                record = Record(
                    user_id=new_user_id,
                    record_date=datetime.strptime(r["record_date"], "%Y-%m-%d").date() if r["record_date"] else datetime.utcnow().date(),
                    type=r["type"],
                    category=r["category"] or "",
                    sub_category=r["sub_category"] or "",
                    amount=r["amount"] or 0,
                    account=r["account"] or "",
                    note=r["note"] or "",
                    created_at=datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S") if r["created_at"] else datetime.utcnow(),
                    updated_at=datetime.strptime(r["updated_at"], "%Y-%m-%d %H:%M:%S") if r["updated_at"] else datetime.utcnow(),
                )
                pg_db.add(record)
            except Exception as e:
                print(f"  跳过记录 {r['id']}: {e}")
        pg_db.commit()
        print(f"记账记录迁移完成，共 {len(records)} 条")

        menus = sqlite_conn.execute("SELECT * FROM menus").fetchall()
        menu_id_map = {}
        for m in menus:
            new_user_id = user_id_map.get(m["user_id"])
            if not new_user_id:
                continue
            menu = Menu(
                user_id=new_user_id,
                parent_id=m["parent_id"] or 0,
                name=m["name"] or "",
                icon=m["icon"] or "",
                sort_order=m["sort_order"] or 0,
                created_at=datetime.strptime(m["created_at"], "%Y-%m-%d %H:%M:%S") if m["created_at"] else datetime.utcnow(),
            )
            pg_db.add(menu)
            pg_db.flush()
            menu_id_map[m["id"]] = menu.id
        pg_db.commit()
        for m in menus:
            if m["parent_id"] and m["parent_id"] in menu_id_map and m["id"] in menu_id_map:
                new_menu = pg_db.query(Menu).filter(Menu.id == menu_id_map[m["id"]]).first()
                if new_menu:
                    new_menu.parent_id = menu_id_map[m["parent_id"]]
        pg_db.commit()
        print(f"菜单迁移完成，共 {len(menus)} 条")

        todos = sqlite_conn.execute("SELECT * FROM todos").fetchall()
        for t in todos:
            new_user_id = user_id_map.get(t["user_id"])
            if not new_user_id:
                continue
            todo = Todo(
                user_id=new_user_id,
                title=t["title"] or "",
                completed=bool(t["completed"]),
                priority=t["priority"] or 0,
                due_date=datetime.strptime(t["due_date"], "%Y-%m-%d").date() if t.get("due_date") else None,
                created_at=datetime.strptime(t["created_at"], "%Y-%m-%d %H:%M:%S") if t["created_at"] else datetime.utcnow(),
                updated_at=datetime.strptime(t["updated_at"], "%Y-%m-%d %H:%M:%S") if t["updated_at"] else datetime.utcnow(),
            )
            pg_db.add(todo)
        pg_db.commit()
        print(f"待办事项迁移完成，共 {len(todos)} 条")

        notes = sqlite_conn.execute("SELECT * FROM notes").fetchall()
        for n in notes:
            new_user_id = user_id_map.get(n["user_id"])
            if not new_user_id:
                continue
            note = Note(
                user_id=new_user_id,
                title=n["title"] or "",
                content=n["content"] or "",
                created_at=datetime.strptime(n["created_at"], "%Y-%m-%d %H:%M:%S") if n["created_at"] else datetime.utcnow(),
                updated_at=datetime.strptime(n["updated_at"], "%Y-%m-%d %H:%M:%S") if n["updated_at"] else datetime.utcnow(),
            )
            pg_db.add(note)
        pg_db.commit()
        print(f"备忘录迁移完成，共 {len(notes)} 条")

        try:
            db_conns = sqlite_conn.execute("SELECT * FROM db_connections").fetchall()
            for dc in db_conns:
                new_user_id = user_id_map.get(dc["user_id"])
                if not new_user_id:
                    continue
                conn = DbConnection(
                    user_id=new_user_id,
                    name=dc["name"] or "",
                    db_type=dc["db_type"] or "",
                    host=dc["host"] or "",
                    port=dc["port"] or 0,
                    username=dc["username"] or "",
                    password=encrypt_password(dc["password"] or ""),
                    database=dc["database"] or "",
                    sqlite_path=dc["sqlite_path"] or "",
                    created_at=datetime.strptime(dc["created_at"], "%Y-%m-%d %H:%M:%S") if dc["created_at"] else datetime.utcnow(),
                    updated_at=datetime.strptime(dc["updated_at"], "%Y-%m-%d %H:%M:%S") if dc["updated_at"] else datetime.utcnow(),
                )
                pg_db.add(conn)
            pg_db.commit()
            print(f"数据库连接配置迁移完成，共 {len(db_conns)} 条")
        except Exception as e:
            print(f"  跳过 db_connections 迁移: {e}")

        print("\n迁移完成！所有用户密码已重置为 Mkld@2026，请登录后修改。")

    finally:
        pg_db.close()
        sqlite_conn.close()


if __name__ == "__main__":
    default_path = Path(__file__).resolve().parent.parent.parent / "data" / "0701_my_project.db"
    sqlite_path = sys.argv[1] if len(sys.argv) > 1 else str(default_path)

    if not Path(sqlite_path).exists():
        print(f"错误：SQLite 文件不存在: {sqlite_path}")
        sys.exit(1)

    migrate_sqlite_to_pg(sqlite_path)
