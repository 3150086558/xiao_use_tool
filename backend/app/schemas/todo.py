from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class TodoBase(BaseModel):
    title: str = Field(..., max_length=200)
    priority: int = 0
    due_date: Optional[date] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None
    due_date: Optional[date] = None


class TodoResponse(TodoBase):
    id: int
    user_id: int
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
