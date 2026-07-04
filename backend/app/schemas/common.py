from pydantic import BaseModel, Field
from datetime import datetime


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict | list | None = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
