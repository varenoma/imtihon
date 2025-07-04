from pydantic import BaseModel, Field
from typing import Optional, List


class ManagementSystemPageBase(BaseModel):
    page: str = Field(
        ...,
        description="Boshqaruv tizimi sahifasining matni. Bo'sh bo'lmasligi kerak."
    )


class ManagementSystemPageCreate(ManagementSystemPageBase):
    pass


class ManagementSystemPageUpdate(ManagementSystemPageBase):
    page: Optional[str] = Field(
        None,
        description="Boshqaruv tizimi sahifasining matni. Ixtiyoriy."
    )


class ManagementSystemPageOut(ManagementSystemPageBase):
    id: int = Field(...,
                    description="Boshqaruv tizimi sahifasining unikal ID raqami.")

    class Config:
        from_attributes = True


class PaginatedManagementSystemPageOut(BaseModel):
    items: List[ManagementSystemPageOut] = Field(
        ..., description="Boshqaruv tizimi sahifalari ro'yxati.")
    total: int = Field(..., description="Umumiy sahifalar soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
