from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class YangilikBase(BaseModel):
    name: str = Field(
        ...,
        description="Yangilikning nomi. Bo'sh bo'lmasligi kerak."
    )
    text: str = Field(
        ...,
        description="Yangilikning matni. Bo'sh bo'lmasligi kerak."
    )
    rasm: str = Field(
        ...,
        description="Rasm faylning serverdagi yo'li (masalan, 'static/images/fayl.jpg'). Majburiy."
    )


class YangilikCreate(YangilikBase):
    pass


class YangilikUpdate(YangilikBase):
    name: Optional[str] = Field(
        None,
        description="Yangilikning nomi. Ixtiyoriy."
    )
    text: Optional[str] = Field(
        None,
        description="Yangilikning matni. Ixtiyoriy."
    )
    rasm: Optional[str] = Field(
        None,
        description="Rasm faylning serverdagi yo'li. Ixtiyoriy, lekin kiritilgan bo'lsa, faqat JPEG yoki PNG fayllar ruxsat etiladi."
    )


class YangilikOut(YangilikBase):
    id: int = Field(..., description="Yangilikning unikal ID raqami.")
    created_at: datetime = Field(..., description="Yangilik yaratilgan vaqt.")

    class Config:
        from_attributes = True


class PaginatedYangilikOut(BaseModel):
    items: List[YangilikOut] = Field(..., description="Yangiliklar ro'yxati.")
    total: int = Field(..., description="Umumiy yangiliklar soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
