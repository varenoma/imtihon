from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class BoglanishFormBase(BaseModel):
    FIO: str = Field(
        ...,
        description="Foydalanuvchining FIOsi. Bo'sh bo'lmasligi kerak."
    )
    email: EmailStr = Field(
        ...,
        description="Foydalanuvchining email manzili. To'g'ri email formatida bo'lishi kerak."
    )
    tel_raqam: str = Field(
        ...,
        description="Telefon raqami. To'g'ri formatda bo'lishi kerak (masalan, +998901234567).",
        pattern=r"^\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$"
    )
    type: str = Field(
        ...,
        description="Murojat turi. Bo'sh bo'lmasligi kerak."
    )
    murojat_matni: str = Field(
        ...,
        description="Murojat matni. Bo'sh bo'lmasligi kerak."
    )
    fayl: Optional[str] = Field(
        None,
        description="Faylning serverdagi yo'li (masalan, 'static/files/fayl.pdf'). Ixtiyoriy, lekin kiritilgan bo'lsa, faqat PDF fayllar ruxsat etiladi."
    )


class BoglanishFormCreate(BoglanishFormBase):
    pass


class BoglanishFormOut(BoglanishFormBase):
    id: int = Field(..., description="Murojat formasining unikal ID raqami.")
    created_at: datetime = Field(..., description="Murojat yaratilgan vaqt.")

    class Config:
        from_attributes = True


class PaginatedBoglanishFormOut(BaseModel):
    items: List[BoglanishFormOut] = Field(...,
                                          description="Murojat formasi ro'yxati.")
    total: int = Field(..., description="Umumiy murojat formasi soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
