from pydantic import BaseModel
from datetime import date


class QonunQarorFarmonOut(BaseModel):
    id: int
    title: str
    type: str
    content: str
    number: str
    date: date
    source: str

    class Config:
        from_attributes = True
