from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DbConnectionBase(BaseModel):
    name: str = Field(..., max_length=100)
    db_type: str = Field(..., max_length=20)
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    database: str = ""
    sqlite_path: str = ""


class DbConnectionCreate(DbConnectionBase):
    pass


class DbConnectionUpdate(BaseModel):
    name: Optional[str] = None
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    sqlite_path: Optional[str] = None


class DbConnectionResponse(BaseModel):
    id: int
    user_id: int
    name: str
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str
    sqlite_path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DbQueryRequestConfig(BaseModel):
    id: Optional[int] = None
    name: str = ""
    db_type: str = Field(..., max_length=20)
    host: str = ""
    port: int = 0
    username: str = ""
    password: str = ""
    database: str = ""
    sqlite_path: str = ""


class DbQueryRequest(BaseModel):
    action: str
    config: DbQueryRequestConfig
    table: Optional[str] = None
    sql: Optional[str] = None
