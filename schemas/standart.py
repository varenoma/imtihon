from pydantic import BaseModel, Field
from typing import Optional, List


class StandartBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255,
                      description="Standart nomi")
    description: Optional[str] = Field(
        None, description="Standart haqida qisqacha ma'lumot")
    pdf: Optional[str] = Field(
        None, description="PDF faylning serverdagi yo'li")


class StandartCreate(StandartBase):
    pass


class StandartUpdate(StandartBase):
    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Standart nomi")


class StandartOut(StandartBase):
    id: int

    class Config:
        from_attributes = True


class PaginatedStandartOut(BaseModel):
    items: List[StandartOut]
    total: int
    page: int
    per_page: int
    total_pages: int
