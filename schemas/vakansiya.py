from pydantic import BaseModel
from datetime import datetime


class VakansiyaOut(BaseModel):
    id: int
    title: str
    description: str
    bolim: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
