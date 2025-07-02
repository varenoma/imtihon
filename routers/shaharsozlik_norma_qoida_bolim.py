import re
from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolim
from schemas.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolimOut
from auth.dependencies import get_current_admin
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

router = APIRouter(prefix="/shaharsozlik-norma-qoida-bolimlar",
                   tags=["Shaharsozlik Norma Qoida Bo'limlari"])

load_dotenv()


class ShaharsozlikNormaQoidaBolimCreate(BaseModel):
    name: str = Field(..., min_length=3,
                      description="Bo'lim nomi, kamida 3 belgi. Masalan: 'Norma bo'limi'")

    @validator("name")
    def validate_name(cls, v):
        return v.strip()


@router.get(
    "/",
    response_model=list[ShaharsozlikNormaQoidaBolimOut],
    summary="Barcha bo'limlarni olish",
    description="Barcha shaharsozlik norma qoida bo'limlarini sahifalarga bo'lib olish. Limit va offset parametrlari yordamida so'rovni boshqarish mumkin.",
    response_description="Bo'limlar ro'yxati, har birida id va nomi."
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(
        10, ge=1, le=100, description="Bir sahifadagi bo'limlar soni (1-100). Masalan: 10"),
    offset: int = Query(
        0, ge=0, description="Qaysi yozuvdan boshlash (0 yoki undan katta). Masalan: 0")
):
    try:
        result = await db.execute(
            select(ShaharsozlikNormaQoidaBolim).offset(offset).limit(
                limit).order_by(ShaharsozlikNormaQoidaBolim.id)
        )
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni olishda xato: {str(e)}")


@router.post(
    "/for_admin/",
    response_model=ShaharsozlikNormaQoidaBolimOut,
    summary="Yangi bo'lim yaratish",
    description="Faqat adminlar uchun: Yangi shaharsozlik norma qoida bo'limi yaratish. Nomi kamida 3 belgidan iborat bo'lishi kerak.",
    response_description="Yaratilgan bo'lim ma'lumotlari."
)
async def create_bolim(
    name: str = Form(...,
                     description="Bo'lim nomi, kamida 3 belgi. Masalan: 'Norma bo'limi'"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = ShaharsozlikNormaQoidaBolimCreate(name=name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    new_bolim = ShaharsozlikNormaQoidaBolim(name=data.name)
    try:
        db.add(new_bolim)
        await db.commit()
        await db.refresh(new_bolim)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni saqlashda xato: {str(e)}")
    return new_bolim


@router.put(
    "/{id}/for_admin/",
    response_model=ShaharsozlikNormaQoidaBolimOut,
    summary="Bo'limni yangilash",
    description="Faqat adminlar uchun: Mavjud bo'limni yangilash. ID orqali bo'lim topiladi va yangi nomi bilan yangilanadi.",
    response_description="Yangilangan bo'lim ma'lumotlari."
)
async def update_bolim(
    id: int,
    name: str = Form(...,
                     description="Bo'lim nomi, kamida 3 belgi. Masalan: 'Norma bo'limi'"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = ShaharsozlikNormaQoidaBolimCreate(name=name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = await db.execute(select(ShaharsozlikNormaQoidaBolim).where(ShaharsozlikNormaQoidaBolim.id == id))
    bolim = result.scalar_one_or_none()
    if not bolim:
        raise HTTPException(status_code=404, detail="Bo'lim topilmadi")

    bolim.name = data.name
    try:
        await db.commit()
        await db.refresh(bolim)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni yangilashda xato: {str(e)}")
    return bolim


@router.delete(
    "/{id}/for_admin/",
    summary="Bo'limni o'chirish",
    description="Faqat adminlar uchun: ID orqali bo'limni o'chirish.",
    response_description="O'chirish muvaffaqiyatli amalga oshirildi."
)
async def delete_bolim(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(ShaharsozlikNormaQoidaBolim).where(ShaharsozlikNormaQoidaBolim.id == id))
    bolim = result.scalar_one_or_none()
    if not bolim:
        raise HTTPException(status_code=404, detail="Bo'lim topilmadi")

    try:
        await db.delete(bolim)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
