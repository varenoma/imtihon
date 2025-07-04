from pydantic import BaseModel, Field
from typing import Optional, List


class ReglamentBase(BaseModel):
    shifri: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Reglamentning shifri (masalan, 'R-001'). Bo'sh bo'lmasligi kerak, 1-100 belgi oralig'ida."
    )
    nomi: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Reglamentning to'liq nomi. Bo'sh bo'lmasligi kerak, 1-255 belgi oralig'ida."
    )
    link: Optional[str] = Field(
        None,
        description="Reglamentga tashqi havola. Ixtiyoriy, lekin kiritilgan bo'lsa, to'g'ri URL bo'lishi kerak (masalan, 'https://example.com')."
    )
    pdf: Optional[str] = Field(
        None,
        description="PDF faylning serverdagi yo'li (masalan, 'static/pdfs/fayl.pdf'). Ixtiyoriy."
    )


class ReglamentCreate(ReglamentBase):
    pass


class ReglamentUpdate(ReglamentBase):
    shifri: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Reglamentning shifri. Ixtiyoriy, agar kiritilgan bo'lsa, 1-100 belgi oralig'ida."
    )
    nomi: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Reglamentning to'liq nomi. Ixtiyoriy, agar kiritilgan bo'lsa, 1-255 belgi oralig'ida."
    )


class ReglamentOut(ReglamentBase):
    id: int = Field(..., description="Reglamentning unikal ID raqami.")

    class Config:
        from_attributes = True


class PaginatedReglamentOut(BaseModel):
    items: List[ReglamentOut] = Field(...,
                                      description="Reglamentlar ro'yxati.")
    total: int = Field(..., description="Umumiy reglamentlar soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
