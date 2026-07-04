from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class MenuResponse(BaseModel):
    id: int
    parent_id: int
    name: str
    icon: str
    sort_order: int
    children: Optional[List["MenuResponse"]] = None

    class Config:
        from_attributes = True


MenuResponse.model_rebuild()
