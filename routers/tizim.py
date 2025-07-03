from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.tizim import Tizim
from models.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolim
from schemas.tizim import TizimCreate, TizimOut
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/tizimlar", tags=["Tizimlar"])


@router.post(
    "/for_admin/",
    response_model=TizimOut,
    summary="Yangi tizim yaratish",
    description="Faqat adminlar uchun: Yangi tizim yaratish. Nom (kamida 1 belgi) majburiy.",
    response_description="Yaratilgan tizim ma'lumotlari."
)
async def create_tizim(
    name: str = Form(..., description="Tizim nomi. Masalan: 'Tizim 1'"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = TizimCreate(name=name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    new_tizim = Tizim(name=data.name)
    try:
        db.add(new_tizim)
        await db.commit()
        await db.refresh(new_tizim)
        return new_tizim
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Tizim yaratishda xato: {str(e)}")


@router.get(
    "/",
    response_model=list[TizimOut],
    summary="Barcha tizimlarni olish",
    description="Barcha tizimlarni sahifalarga bo'lib olish. Limit va offset parametrlari yordamida so'rovni boshqarish mumkin.",
    response_description="Tizimlar ro'yxati, har birida id, nom va yaratilgan vaqt."
)
async def get_all_tizimlar(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(
        10, ge=1, le=100, description="Bir sahifadagi tizimlar soni (1-100). Masalan: 10"),
    offset: int = Query(
        0, ge=0, description="Qaysi yozuvdan boshlash (0 yoki undan katta). Masalan: 0")
):
    try:
        result = await db.execute(
            select(Tizim).offset(offset).limit(limit).order_by(Tizim.id)
        )
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni olishda xato: {str(e)}")


@router.put(
    "/{id}/for_admin/",
    response_model=TizimOut,
    summary="Tizimni yangilash",
    description="Faqat adminlar uchun: Mavjud tizimni yangilash. ID orqali tizim topiladi va yangi nom bilan yangilanadi.",
    response_description="Yangilangan tizim ma'lumotlari."
)
async def update_tizim(
    id: int,
    name: str = Form(..., description="Tizim nomi. Masalan: 'Tizim 1'"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = TizimCreate(name=name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = await db.execute(select(Tizim).where(Tizim.id == id))
    tizim = result.scalar_one_or_none()
    if not tizim:
        raise HTTPException(status_code=404, detail="Tizim topilmadi")

    tizim.name = data.name
    try:
        await db.commit()
        await db.refresh(tizim)
        return tizim
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Tizimni yangilashda xato: {str(e)}")


@router.delete(
    "/{id}/for_admin/",
    summary="Tizimni o'chirish",
    description="Faqat adminlar uchun: ID orqali tizimni o'chirish. Agar tizimga bog'langan bo'limlar mavjud bo'lsa, o'chirish rad etiladi.",
    response_description="O'chirish muvaffaqiyatli amalga oshirildi."
)
async def delete_tizim(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(Tizim).where(Tizim.id == id))
    tizim = result.scalar_one_or_none()
    if not tizim:
        raise HTTPException(status_code=404, detail="Tizim topilmadi")

    # Bog'langan bo'limlarni tekshirish
    result = await db.execute(
        select(ShaharsozlikNormaQoidaBolim).where(
            ShaharsozlikNormaQoidaBolim.tizim == id)
    )
    bolimlar = result.scalars().all()
    if bolimlar:
        raise HTTPException(
            status_code=400,
            detail="Tizim o'chirib bo'lmaydi, chunki unga bog'langan bo'limlar mavjud."
        )

    try:
        await db.delete(tizim)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Tizimni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
