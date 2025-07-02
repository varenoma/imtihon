import re
from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.vakansiyalar import Vakansiya
from schemas.vakansiya import VakansiyaOut
from auth.dependencies import get_current_admin
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, validator

router = APIRouter(prefix="/vakansiyalar", tags=["Vakansiyalar"])

load_dotenv()


class VakansiyaCreate(BaseModel):
    title: str
    description: str
    bolim: str
    is_active: bool = True

    @validator("title")
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError(
                "Vakansiya nomi kamida 5 belgidan iborat bo'lishi kerak. Masalan: 'Backend dasturchi'")
        return v.strip()

    @validator("description")
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError(
                "Tavsif kamida 10 belgidan iborat bo'lishi kerak. Masalan: 'Python va FastAPI bilan ishlash'")
        return v.strip()

    @validator("bolim")
    def validate_bolim(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "Bo'lim nomi kamida 3 belgidan iborat bo'lishi kerak. Masalan: 'IT bo'limi'")
        return v.strip()


@router.get(
    "/",
    response_model=list[VakansiyaOut],
    summary="Barcha vakansiyalarni olish",
    description="Barcha vakansiyalarni sahifalarga bo'lib olish. Limit (bir sahifadagi yozuvlar soni) va offset (qaysi yozuvdan boshlash) parametrlari yordamida so'rovni boshqarish mumkin. Vakansiyalar yaratilgan vaqt bo'yicha kamayish tartibida qaytariladi.",
    response_description="Vakansiyalar ro'yxati, har birida id, nomi, tavsifi, bo'limi, aktivligi va yaratilgan vaqti."
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Bir sahifadagi vakansiyalar soni (1-100). Masalan: 10"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Qaysi yozuvdan boshlash (0 yoki undan katta). Masalan: 0"
    )
):
    try:
        result = await db.execute(
            select(Vakansiya).offset(offset).limit(
                limit).order_by(Vakansiya.created_at.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni olishda xato: {str(e)}")


@router.post(
    "/for_admin/",
    response_model=VakansiyaOut,
    summary="Yangi vakansiya yaratish",
    description="Faqat adminlar uchun: Yangi vakansiya yaratish. Barcha maydonlar (title, description, bolim) majburiy, is_active ixtiyoriy (sukut bo'yicha True). Yaratilgan vaqt avtomatik o'rnatiladi.",
    response_description="Yaratilgan vakansiya ma'lumotlari."
)
async def create_vakansiya(
    title: str = Form(..., description="Vakansiya nomi, kamida 5 belgi. Masalan: 'Backend dasturchi'"),
    description: str = Form(
        ..., description="Vakansiya tavsifi, kamida 10 belgi. Masalan: 'Python va FastAPI bilan ishlash'"),
    bolim: str = Form(...,
                      description="Bo'lim nomi, kamida 3 belgi. Masalan: 'IT bo'limi'"),
    is_active: bool = Form(
        True, description="Vakansiya aktivligi (True/False). Masalan: true"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = VakansiyaCreate(
            title=title,
            description=description,
            bolim=bolim,
            is_active=is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    new_vakansiya = Vakansiya(
        title=data.title,
        description=data.description,
        bolim=data.bolim,
        is_active=data.is_active,
        created_at=datetime.utcnow()
    )
    try:
        db.add(new_vakansiya)
        await db.commit()
        await db.refresh(new_vakansiya)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni saqlashda xato: {str(e)}")
    return new_vakansiya


@router.put(
    "/{id}/for_admin/",
    response_model=VakansiyaOut,
    summary="Vakansiyani yangilash",
    description="Faqat adminlar uchun: Mavjud vakansiyani yangilash. ID orqali vakansiya topiladi va yangi ma'lumotlar (title, description, bolim, is_active) bilan yangilanadi. Yaratilgan vaqt o'zgarmaydi.",
    response_description="Yangilangan vakansiya ma'lumotlari."
)
async def update_vakansiya(
    id: int,
    title: str = Form(..., description="Vakansiya nomi, kamida 5 belgi. Masalan: 'Backend dasturchi'"),
    description: str = Form(
        ..., description="Vakansiya tavsifi, kamida 10 belgi. Masalan: 'Python va FastAPI bilan ishlash'"),
    bolim: str = Form(...,
                      description="Bo'lim nomi, kamida 3 belgi. Masalan: 'IT bo'limi'"),
    is_active: bool = Form(
        True, description="Vakansiya aktivligi (True/False). Masalan: true"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = VakansiyaCreate(
            title=title,
            description=description,
            bolim=bolim,
            is_active=is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = await db.execute(select(Vakansiya).where(Vakansiya.id == id))
    vakansiya = result.scalar_one_or_none()
    if not vakansiya:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    vakansiya.title = data.title
    vakansiya.description = data.description
    vakansiya.bolim = data.bolim
    vakansiya.is_active = data.is_active

    try:
        await db.commit()
        await db.refresh(vakansiya)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni yangilashda xato: {str(e)}")
    return vakansiya


@router.delete(
    "/{id}/for_admin/",
    summary="Vakansiyani o'chirish",
    description="Faqat adminlar uchun: ID orqali vakansiyani o'chirish.",
    response_description="O'chirish muvaffaqiyatli amalga oshirildi."
)
async def delete_vakansiya(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(Vakansiya).where(Vakansiya.id == id))
    vakansiya = result.scalar_one_or_none()
    if not vakansiya:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    try:
        await db.delete(vakansiya)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
