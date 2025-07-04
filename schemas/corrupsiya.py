from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CorrupsiyaBase(BaseModel):
    name: str = Field(
        ...,
        description="Korrupsiyaga qarshi yozuvning nomi. Bo'sh bo'lmasligi kerak."
    )
    description: str = Field(
        ...,
        description="Korrupsiyaga qarshi yozuvning tavsifi. Bo'sh bo'lmasligi kerak."
    )


class CorrupsiyaCreate(CorrupsiyaBase):
    pass


class CorrupsiyaUpdate(CorrupsiyaBase):
    name: Optional[str] = Field(
        None,
        description="Korrupsiyaga qarshi yozuvning nomi. Ixtiyoriy."
    )
    description: Optional[str] = Field(
        None,
        description="Korrupsiyaga qarshi yozuvning tavsifi. Ixtiyoriy."
    )


class CorrupsiyaOut(CorrupsiyaBase):
    id: int = Field(...,
                    description="Korrupsiyaga qarshi yozuvning unikal ID raqami.")
    created_at: datetime = Field(..., description="Yozuv yaratilgan vaqt.")

    class Config:
        from_attributes = True


class PaginatedCorrupsiyaOut(BaseModel):
    items: List[CorrupsiyaOut] = Field(...,
                                       description="Korrupsiyaga qarshi yozuvlar ro'yxati.")
    total: int = Field(..., description="Umumiy yozuvlar soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
