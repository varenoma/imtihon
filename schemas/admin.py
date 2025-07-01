from pydantic import BaseModel
from datetime import datetime


class AdminOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
