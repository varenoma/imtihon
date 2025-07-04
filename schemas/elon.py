from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ElonBase(BaseModel):
    name: str = Field(
        ...,
        description="E'lonning nomi. Bo'sh bo'lmasligi kerak."
    )
    description: str = Field(
        ...,
        description="E'lonning tavsifi. Bo'sh bo'lmasligi kerak."
    )
    rasm: str = Field(
        ...,
        description="Rasm faylning serverdagi yo'li (masalan, 'static/images/fayl.jpg'). Majburiy."
    )


class ElonCreate(ElonBase):
    pass


class ElonUpdate(ElonBase):
    name: Optional[str] = Field(
        None,
        description="E'lonning nomi. Ixtiyoriy."
    )
    description: Optional[str] = Field(
        None,
        description="E'lonning tavsifi. Ixtiyoriy."
    )
    rasm: Optional[str] = Field(
        None,
        description="Rasm faylning serverdagi yo'li. Ixtiyoriy, lekin kiritilgan bo'lsa, faqat JPEG yoki PNG fayllar ruxsat etiladi."
    )


class ElonOut(ElonBase):
    id: int = Field(..., description="E'lonning unikal ID raqami.")
    created_at: datetime = Field(..., description="E'lon yaratilgan vaqt.")

    class Config:
        from_attributes = True


class PaginatedElonOut(BaseModel):
    items: List[ElonOut] = Field(..., description="E'lonlar ro'yxati.")
    total: int = Field(..., description="Umumiy e'lonlar soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
