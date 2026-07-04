from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Numeric, DateTime, ForeignKey, Index
from ..database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    type = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    sub_category = Column(String(50), default="")
    amount = Column(Numeric(12, 2), nullable=False)
    account = Column(String(50), default="")
    note = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_records_user_date", "user_id", "record_date"),
    )
