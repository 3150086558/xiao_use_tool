from pydantic import BaseModel
from datetime import datetime


class UserAdminResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime
    record_count: int = 0
    todo_count: int = 0
    note_count: int = 0

    class Config:
        from_attributes = True


class ResetPasswordRequest(BaseModel):
    new_password: str
