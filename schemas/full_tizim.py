from pydantic import BaseModel
from datetime import datetime
from typing import List


class GuruhSchema(BaseModel):
    id: int
    shifr: str
    hujjat_nomi: str
    link: str
    pdf: str
    created_at: datetime

    class Config:
        from_attributes = True


class BolimSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    guruhlar: List[GuruhSchema] = []

    class Config:
        from_attributes = True


class FullTizimSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    bolimlar: List[BolimSchema] = []

    class Config:
        from_attributes = True
