from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ..database import Base


class DbConnection(Base):
    __tablename__ = "db_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    db_type = Column(String(20), nullable=False)
    host = Column(String(100), default="")
    port = Column(Integer, default=0)
    username = Column(String(100), default="")
    password = Column(String(500), default="")
    database = Column(String(100), default="")
    sqlite_path = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
