from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class MenuBase(BaseModel):
    title: str = Field(
        ...,
        description="Menu nomi. Bo'sh bo'lmasligi va 255 belgidan oshmasligi kerak.",
        min_length=1,
        max_length=255
    )
    url: Optional[str] = Field(
        None,
        description="Menu URL manzili (ixtiyoriy). To'g'ri URL formatida bo'lishi kerak (masalan, /path yoki https://example.com).",
        max_length=255
    )


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    title: Optional[str] = Field(
        None,
        description="Menu nomi. Ixtiyoriy, lekin kiritilgan bo'lsa, bo'sh bo'lmasligi va 255 belgidan oshmasligi kerak.",
        min_length=1,
        max_length=255
    )


class MenuOut(MenuBase):
    id: int = Field(..., description="Menu unikal ID raqami.")
    created_at: datetime = Field(..., description="Menu yaratilgan vaqt.")
    submenus: List["SubMenuOut"] = Field(...,
                                         description="Menu ostidagi submenular ro'yxati.")

    class Config:
        from_attributes = True


class SubMenuBase(BaseModel):
    title: str = Field(
        ...,
        description="Submenu nomi. Bo'sh bo'lmasligi va 255 belgidan oshmasligi kerak.",
        min_length=1,
        max_length=255
    )
    url: Optional[str] = Field(
        None,
        description="Submenu URL manzili (ixtiyoriy). To'g'ri URL formatida bo'lishi kerak (masalan, /path yoki https://example.com).",
        max_length=255
    )
    menu_id: int = Field(..., description="Submenu bog'langan menu ID raqami.")


class SubMenuCreate(SubMenuBase):
    pass


class SubMenuUpdate(SubMenuBase):
    title: Optional[str] = Field(
        None,
        description="Submenu nomi. Ixtiyoriy, lekin kiritilgan bo'lsa, bo'sh bo'lmasligi va 255 belgidan oshmasligi kerak.",
        min_length=1,
        max_length=255
    )
    url: Optional[str] = Field(
        None,
        description="Submenu URL manzili (ixtiyoriy).",
        max_length=255
    )
    menu_id: Optional[int] = Field(
        None,
        description="Submenu bog'langan menu ID raqami. Ixtiyoriy."
    )


class SubMenuOut(SubMenuBase):
    id: int = Field(..., description="Submenu unikal ID raqami.")
    created_at: datetime = Field(..., description="Submenu yaratilgan vaqt.")

    class Config:
        from_attributes = True


class PaginatedMenuOut(BaseModel):
    items: List[MenuOut] = Field(..., description="Menular ro'yxati.")
    total: int = Field(..., description="Umumiy menular soni.")
    page: int = Field(..., description="Joriy sahifa raqami.")
    per_page: int = Field(...,
                          description="Har bir sahifadagi elementlar soni.")
    total_pages: int = Field(..., description="Umumiy sahifalar soni.")
