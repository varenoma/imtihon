from pydantic import BaseModel, Field
from typing import Optional, List


class MalumotnomaBase(BaseModel):
    nomi: str = Field(
        ...,
        description="Ma'lumotnoma nomi. Bo'sh bo'lmasligi kerak."
    )
    hujjat: str = Field(
        ...,
        description="PDF faylning serverdagi yo'li (masalan, 'static/pdfs/fayl.pdf'). Majburiy."
    )


class MalumotnomaCreate(MalumotnomaBase):
    pass


class MalumotnomaUpdate(MalumotnomaBase):
    nomi: Optional[str] = Field(
        None,
        description="Ma'lumotnoma nomi. Ixtiyoriy."
    )
    hujjat: Optional[str] = Field(
        None,
        description="PDF faylning serverdagi yo'li. Ixtiyoriy, lekin kiritilgan bo'lsa, faqat PDF fayllar ruxsat etiladi."
    )


class MalumotnomaOut(MalumotnomaBase):
    id: int = Field(..., description="Ma'lumotnomaning unikal ID raqami.")

    class Config:
        from_attributes = True


class PaginatedMalumotnomaOut(BaseModel):
    items: List[MalumotnomaOut] = Field(...,
                                        description="Ma'lumotnomalar ro'yxati.")
    total: int = Field(..., description="Umumiy ma'lumotnomalar soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
