from pydantic import BaseModel, Field
from typing import Optional, List


class SmetaResursNormaBase(BaseModel):
    yangi_ShNQ_raqami: str = Field(
        ...,
        description="Yangi ShNQ raqami. Bo'sh bo'lmasligi kerak."
    )
    yangilangan_ShNQ_nomi: str = Field(
        ...,
        description="Yangilangan ShNQ nomi. Bo'sh bo'lmasligi kerak."
    )
    ShNQ_raqami: str = Field(
        ...,
        description="ShNQ raqami. Bo'sh bo'lmasligi kerak."
    )
    ShNQ_nomi: str = Field(
        ...,
        description="ShNQ nomi. Bo'sh bo'lmasligi kerak."
    )
    pdf: Optional[str] = Field(
        None,
        description="PDF faylning serverdagi yo'li (masalan, 'static/pdfs/fayl.pdf'). Ixtiyoriy."
    )


class SmetaResursNormaCreate(SmetaResursNormaBase):
    pass


class SmetaResursNormaUpdate(SmetaResursNormaBase):
    yangi_ShNQ_raqami: Optional[str] = Field(
        None,
        description="Yangi ShNQ raqami. Ixtiyoriy."
    )
    yangilangan_ShNQ_nomi: Optional[str] = Field(
        None,
        description="Yangilangan ShNQ nomi. Ixtiyoriy."
    )
    ShNQ_raqami: Optional[str] = Field(
        None,
        description="ShNQ raqami. Ixtiyoriy."
    )
    ShNQ_nomi: Optional[str] = Field(
        None,
        description="ShNQ nomi. Ixtiyoriy."
    )


class SmetaResursNormaOut(SmetaResursNormaBase):
    id: int = Field(...,
                    description="Smeta resurs normasining unikal ID raqami.")

    class Config:
        from_attributes = True


class PaginatedSmetaResursNormaOut(BaseModel):
    items: List[SmetaResursNormaOut] = Field(
        ..., description="Smeta resurs normalari ro'yxati.")
    total: int = Field(..., description="Umumiy smeta resurs normalari soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
