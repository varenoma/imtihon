from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class TmsitiBoglanishMalumotiBase(BaseModel):
    joylashuv: str = Field(
        ...,
        description="Joylashuv ma'lumoti. Bo'sh bo'lmasligi kerak."
    )
    manzil: str = Field(
        ...,
        description="Manzil ma'lumoti. Bo'sh bo'lmasligi kerak."
    )
    email: EmailStr = Field(
        ...,
        description="Asosiy email manzili. To'g'ri email formatida bo'lishi kerak."
    )
    qoshimcha_email: EmailStr = Field(
        ...,
        description="Qo'shimcha email manzili. To'g'ri email formatida bo'lishi kerak."
    )
    tel_raqam: str = Field(
        ...,
        description="Telefon raqami. To'g'ri formatda bo'lishi kerak (masalan, +998901234567).",
        pattern=r"^\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$"
    )


class TmsitiBoglanishMalumotiCreate(TmsitiBoglanishMalumotiBase):
    pass


class TmsitiBoglanishMalumotiUpdate(TmsitiBoglanishMalumotiBase):
    joylashuv: Optional[str] = Field(
        None,
        description="Joylashuv ma'lumoti. Ixtiyoriy."
    )
    manzil: Optional[str] = Field(
        None,
        description="Manzil ma'lumoti. Ixtiyoriy."
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Asosiy email manzili. Ixtiyoriy, lekin kiritilgan bo'lsa, to'g'ri email formatida bo'lishi kerak."
    )
    qoshimcha_email: Optional[EmailStr] = Field(
        None,
        description="Qo'shimcha email manzili. Ixtiyoriy, lekin kiritilgan bo'lsa, to'g'ri email formatida bo'lishi kerak."
    )
    tel_raqam: Optional[str] = Field(
        None,
        description="Telefon raqami. Ixtiyoriy, lekin kiritilgan bo'lsa, to'g'ri formatda bo'lishi kerak (masalan, +998901234567).",
        pattern=r"^\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$"
    )


class TmsitiBoglanishMalumotiOut(TmsitiBoglanishMalumotiBase):
    id: int = Field(...,
                    description="Bog'lanish ma'lumotining unikal ID raqami.")

    class Config:
        from_attributes = True


class PaginatedTmsitiBoglanishMalumotiOut(BaseModel):
    items: List[TmsitiBoglanishMalumotiOut] = Field(
        ..., description="Bog'lanish ma'lumotlari ro'yxati.")
    total: int = Field(..., description="Umumiy bog'lanish ma'lumotlari soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
