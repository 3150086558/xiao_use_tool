from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class RecordBase(BaseModel):
    record_date: date
    type: str = Field(..., pattern=r'^(income|expense)$')
    category: str = Field(..., max_length=50)
    sub_category: Optional[str] = ""
    amount: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)
    account: Optional[str] = ""
    note: Optional[str] = ""


class RecordCreate(RecordBase):
    pass


class RecordUpdate(RecordBase):
    pass


class RecordResponse(RecordBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    income: float
    expense: float
    balance: float
    categories: list[dict]


class RecordStatsResponse(BaseModel):
    monthly_trend: list[dict]
    category_pie: list[dict]
    top_categories: list[dict]
