from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload  # Added import
from core.database import get_db
from models.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolim
from models.tizim import Tizim
from models.guruh import Guruh
from schemas.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolimCreate, ShaharsozlikNormaQoidaBolimOut
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/shaharsozlik-norma-qoida-bolimlar",
                   tags=["ShaharsozlikNormaQoidaBolimlar"])


@router.post(
    "/for_admin/",
    response_model=ShaharsozlikNormaQoidaBolimOut,
    summary="Yangi bo'lim yaratish",
    description="Faqat adminlar uchun: Yangi bo'lim yaratish. Nom (kamida 1 belgi) va tizim (mavjud tizim ID'si) majburiy.",
    response_description="Yaratilgan bo'lim ma'lumotlari."
)
async def create_bolim(
    name: str = Form(..., description="Bo'lim nomi. Masalan: 'Norma bo'limi'"),
    tizim: int = Form(..., description="Tizim ID'si. Masalan: 1"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = ShaharsozlikNormaQoidaBolimCreate(name=name, tizim=tizim)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Tizim mavjudligini tekshirish
    result = await db.execute(select(Tizim).where(Tizim.id == tizim))
    tizim_obj = result.scalar_one_or_none()
    if not tizim_obj:
        raise HTTPException(status_code=404, detail="Tizim topilmadi")

    new_bolim = ShaharsozlikNormaQoidaBolim(name=data.name, tizim=data.tizim)
    try:
        db.add(new_bolim)
        await db.commit()
        await db.refresh(new_bolim)
        # Explicitly load tizim_obj after refresh
        result = await db.execute(
            select(ShaharsozlikNormaQoidaBolim)
            .options(joinedload(ShaharsozlikNormaQoidaBolim.tizim_obj))
            .where(ShaharsozlikNormaQoidaBolim.id == new_bolim.id)
        )
        new_bolim = result.scalar_one()
        return new_bolim
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Bo'lim yaratishda xato: {str(e)}")


@router.get(
    "/",
    response_model=list[ShaharsozlikNormaQoidaBolimOut],
    summary="Barcha bo'limlarni olish",
    description="Barcha bo'limlarni yoki ma'lum bir tizimga tegishli bo'limlarni sahifalarga bo'lib olish. Limit, offset va ixtiyoriy tizim parametri yordamida so'rovni boshqarish mumkin.",
    response_description="Bo'limlar ro'yxati, har birida id, nom, tizim ID'si, yaratilgan vaqt va tizim ma'lumotlari."
)
async def get_all_bolimlar(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(
        10, ge=1, le=100, description="Bir sahifadagi bo'limlar soni (1-100). Masalan: 10"),
    offset: int = Query(
        0, ge=0, description="Qaysi yozuvdan boshlash (0 yoki undan katta). Masalan: 0"),
    tizim: int | None = Query(
        None, description="Tizim ID'si bo'yicha filtr. Masalan: 1. Agar berilmasa, barcha bo'limlar qaytariladi.")
):
    try:
        # Tizim mavjudligini tekshirish, agar berilgan bo'lsa
        if tizim is not None:
            result = await db.execute(select(Tizim).where(Tizim.id == tizim))
            tizim_obj = result.scalar_one_or_none()
            if not tizim_obj:
                raise HTTPException(
                    status_code=404, detail=f"Tizim ID'si {tizim} topilmadi")

        # Bo'limlar so'rovi
        query = select(ShaharsozlikNormaQoidaBolim).options(joinedload(ShaharsozlikNormaQoidaBolim.tizim_obj)).offset(
            offset).limit(limit).order_by(ShaharsozlikNormaQoidaBolim.id)
        if tizim is not None:
            query = query.where(ShaharsozlikNormaQoidaBolim.tizim == tizim)

        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni olishda xato: {str(e)}")


@router.put(
    "/{id}/for_admin/",
    response_model=ShaharsozlikNormaQoidaBolimOut,
    summary="Bo'limni yangilash",
    description="Faqat adminlar uchun: Mavjud bo'limni yangilash. ID orqali bo'lim topiladi va yangi nom va tizim ID'si bilan yangilanadi.",
    response_description="Yangilangan bo'lim ma'lumotlari."
)
async def update_bolim(
    id: int,
    name: str = Form(..., description="Bo'lim nomi. Masalan: 'Norma bo'limi'"),
    tizim: int = Form(..., description="Tizim ID'si. Masalan: 1"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = ShaharsozlikNormaQoidaBolimCreate(name=name, tizim=tizim)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Bo'limni topish
    result = await db.execute(select(ShaharsozlikNormaQoidaBolim).where(ShaharsozlikNormaQoidaBolim.id == id))
    bolim = result.scalar_one_or_none()
    if not bolim:
        raise HTTPException(status_code=404, detail="Bo'lim topilmadi")

    # Tizim mavjudligini tekshirish
    result = await db.execute(select(Tizim).where(Tizim.id == tizim))
    tizim_obj = result.scalar_one_or_none()
    if not tizim_obj:
        raise HTTPException(status_code=404, detail="Tizim topilmadi")

    bolim.name = data.name
    bolim.tizim = data.tizim
    try:
        await db.commit()
        await db.refresh(bolim)
        # Explicitly load tizim_obj after refresh
        result = await db.execute(
            select(ShaharsozlikNormaQoidaBolim)
            .options(joinedload(ShaharsozlikNormaQoidaBolim.tizim_obj))
            .where(ShaharsozlikNormaQoidaBolim.id == bolim.id)
        )
        bolim = result.scalar_one()
        return bolim
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Bo'limni yangilashda xato: {str(e)}")


@router.delete(
    "/{id}/for_admin/",
    summary="Bo'limni o'chirish",
    description="Faqat adminlar uchun: ID orqali bo'limni o'chirish. Agar bo'limga bog'langan guruhlar mavjud bo'lsa, o'chirish rad etiladi.",
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

    # Bog'langan guruhlarni tekshirish
    result = await db.execute(select(Guruh).where(Guruh.bolim == id))
    guruhlar = result.scalars().all()
    if guruhlar:
        raise HTTPException(
            status_code=400,
            detail="Bo'lim o'chirib bo'lmaydi, chunki unga bog'langan guruhlar mavjud."
        )

    try:
        await db.delete(bolim)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Bo'limni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
