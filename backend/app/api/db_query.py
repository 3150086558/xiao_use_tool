import re
import socket
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.user import User
from ..models.db_connection import DbConnection
from ..schemas.db_query import (
    DbConnectionCreate, DbConnectionUpdate, DbConnectionResponse, DbQueryRequest
)
from ..utils.crypto import encrypt_password, decrypt_password
from ..deps import get_current_user

router = APIRouter()


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ALLOWED_SQL_PREFIXES = ("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "WITH")


def _mask_password(conn: DbConnection) -> dict:
    data = DbConnectionResponse.model_validate(conn).model_dump()
    if data["password"]:
        data["password"] = "******"
    return data


@router.get("/connections", response_model=list[dict])
def list_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    items = db.query(DbConnection).filter(
        DbConnection.user_id == current_user.id
    ).order_by(DbConnection.id.desc()).all()
    return [_mask_password(item) for item in items]


@router.post("/connections", response_model=dict, status_code=201)
def create_connection(
    data: DbConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    conn = DbConnection(
        user_id=current_user.id,
        name=data.name,
        db_type=data.db_type,
        host=data.host,
        port=data.port,
        username=data.username,
        password=encrypt_password(data.password) if data.password else "",
        database=data.database,
        sqlite_path=data.sqlite_path,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return _mask_password(conn)


@router.put("/connections/{conn_id}", response_model=dict)
def update_connection(
    conn_id: int,
    data: DbConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    conn = db.query(DbConnection).filter(
        DbConnection.id == conn_id, DbConnection.user_id == current_user.id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="连接不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password":
            if value and value != "******":
                conn.password = encrypt_password(value)
        else:
            setattr(conn, key, value)
    db.commit()
    db.refresh(conn)
    return _mask_password(conn)


@router.delete("/connections/{conn_id}")
def delete_connection(
    conn_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    conn = db.query(DbConnection).filter(
        DbConnection.id == conn_id, DbConnection.user_id == current_user.id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="连接不存在")
    db.delete(conn)
    db.commit()
    return {"ok": True}


def _resolve_password(config: dict, user_id: int, db: Session) -> str:
    pw = config.get("password", "")
    if pw and pw != "******":
        return pw
    if config.get("id"):
        conn = db.query(DbConnection).filter(
            DbConnection.id == config["id"],
            DbConnection.user_id == user_id,
        ).first()
        if conn:
            return decrypt_password(conn.password)
    return ""


def _test_port_open(host: str, port: int, timeout: int = 3) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def _get_db_conn(db_type: str, host: str, port: int, username: str, password: str, database: str, sqlite_path: str = ""):
    if db_type == "postgres":
        import psycopg2
        return psycopg2.connect(host=host, port=port, dbname=database, user=username, password=password)
    elif db_type == "mysql":
        import pymysql
        return pymysql.connect(host=host, port=port, user=username, password=password, database=database, autocommit=True)
    elif db_type == "sqlite":
        import sqlite3
        return sqlite3.connect(sqlite_path)
    else:
        raise ValueError(f"不支持的数据库类型：{db_type}")


@router.post("/{action}")
def db_query(
    action: str,
    data: DbQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(_get_db),
):
    config = data.config
    password = _resolve_password(config.model_dump(), current_user.id, db)
    db_type = config.db_type
    host = config.host
    port = config.port or (5432 if db_type == "postgres" else 3306)
    username = config.username
    database = config.database
    sqlite_path = config.sqlite_path

    if action == "connect":
        if db_type in ("postgres", "mysql"):
            if not _test_port_open(host, port):
                raise HTTPException(status_code=400, detail=f"无法连接到 {host}:{port}，请检查主机和端口")
        try:
            conn = _get_db_conn(db_type, host, port, username, password, database, sqlite_path)
            conn.close()
            return {"ok": True, "message": "连接成功"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"连接失败：{str(e)}")

    if action == "tables":
        try:
            conn = _get_db_conn(db_type, host, port, username, password, database, sqlite_path)
            cur = conn.cursor()
            if db_type == "postgres":
                cur.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public' ORDER BY table_name
                """)
            elif db_type == "mysql":
                cur.execute("SHOW TABLES")
            else:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cur.fetchall()]
            conn.close()
            return {"tables": tables}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"获取表列表失败：{str(e)}")

    if action == "schema":
        table = data.table
        if not table:
            raise HTTPException(status_code=400, detail="缺少表名参数")
        if not re.match(r'^[a-zA-Z0-9_]+$', table):
            raise HTTPException(status_code=400, detail="表名包含非法字符")
        try:
            conn = _get_db_conn(db_type, host, port, username, password, database, sqlite_path)
            cur = conn.cursor()
            if db_type == "postgres":
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                columns = [
                    {"name": r[0], "type": r[1], "nullable": r[2] == "YES", "default": r[3]}
                    for r in cur.fetchall()
                ]
            elif db_type == "mysql":
                cur.execute(f"DESCRIBE `{table}`")
                columns = [
                    {"name": r[0], "type": r[1], "nullable": r[2] == "YES", "default": r[4]}
                    for r in cur.fetchall()
                ]
            else:
                cur.execute(f'PRAGMA table_info("{table}")')
                columns = [
                    {"name": r[1], "type": r[2], "nullable": r[3] == 0, "default": r[4]}
                    for r in cur.fetchall()
                ]
            conn.close()
            return {"table": table, "columns": columns}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"获取表结构失败：{str(e)}")

    if action == "query":
        sql = (data.sql or "").strip()
        if not sql:
            raise HTTPException(status_code=400, detail="SQL 语句不能为空")
        first_word = sql.split()[0].upper() if sql.split() else ""
        if first_word not in ALLOWED_SQL_PREFIXES:
            raise HTTPException(status_code=400, detail=f"不允许执行 {first_word} 语句，仅支持查询类语句")
        try:
            conn = _get_db_conn(db_type, host, port, username, password, database, sqlite_path)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                result = [dict(zip(columns, row)) for row in rows]
            else:
                result = []
            conn.close()
            return {"columns": [desc[0] for desc in cur.description] if cur.description else [], "rows": result, "count": len(rows)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"查询失败：{str(e)}")

    raise HTTPException(status_code=400, detail=f"不支持的操作：{action}")
