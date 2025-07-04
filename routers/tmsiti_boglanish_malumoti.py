from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.tmsiti_boglanish_malumoti import TmsitiBoglanishMalumoti
from schemas.tmsiti_boglanish_malumoti import TmsitiBoglanishMalumotiCreate, TmsitiBoglanishMalumotiUpdate, TmsitiBoglanishMalumotiOut, PaginatedTmsitiBoglanishMalumotiOut
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/tmsiti_boglanish_malumoti",
                   tags=["TMSITI Bog'lanish Ma'lumotlari"])


@router.get("/", response_model=PaginatedTmsitiBoglanishMalumotiOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(TmsitiBoglanishMalumoti))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(TmsitiBoglanishMalumoti).offset(offset).limit(
                per_page).order_by(TmsitiBoglanishMalumoti.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedTmsitiBoglanishMalumotiOut(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ma'lumotlarni olishda xato yuz berdi: {str(e)}"
        )


@router.post("/for_admin/", response_model=TmsitiBoglanishMalumotiOut)
async def create(
    joylashuv: str = Form(..., description="Joylashuv ma'lumoti"),
    manzil: str = Form(..., description="Manzil ma'lumoti"),
    email: str = Form(..., description="Asosiy email manzili"),
    qoshimcha_email: str = Form(..., description="Qo'shimcha email manzili"),
    tel_raqam: str = Form(..., description="Telefon raqami"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # TmsitiBoglanishMalumotiCreate schemaga ma'lumotlarni yuborish
        boglanish_data = TmsitiBoglanishMalumotiCreate(
            joylashuv=joylashuv,
            manzil=manzil,
            email=email,
            qoshimcha_email=qoshimcha_email,
            tel_raqam=tel_raqam
        )

        new_boglanish = TmsitiBoglanishMalumoti(
            joylashuv=boglanish_data.joylashuv,
            manzil=boglanish_data.manzil,
            email=boglanish_data.email,
            qoshimcha_email=boglanish_data.qoshimcha_email,
            tel_raqam=boglanish_data.tel_raqam
        )
        db.add(new_boglanish)
        await db.commit()
        await db.refresh(new_boglanish)
        return new_boglanish
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bog'lanish ma'lumoti yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=TmsitiBoglanishMalumotiOut)
async def update(
    id: int,
    joylashuv: str = Form(None, description="Joylashuv ma'lumoti (ixtiyoriy)"),
    manzil: str = Form(None, description="Manzil ma'lumoti (ixtiyoriy)"),
    email: str = Form(None, description="Asosiy email manzili (ixtiyoriy)"),
    qoshimcha_email: str = Form(
        None, description="Qo'shimcha email manzili (ixtiyoriy)"),
    tel_raqam: str = Form(None, description="Telefon raqami (ixtiyoriy)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # TmsitiBoglanishMalumotiUpdate schemaga ma'lumotlarni yuborish
        boglanish_data = TmsitiBoglanishMalumotiUpdate(
            joylashuv=joylashuv,
            manzil=manzil,
            email=email,
            qoshimcha_email=qoshimcha_email,
            tel_raqam=tel_raqam
        )

        result = await db.execute(select(TmsitiBoglanishMalumoti).where(TmsitiBoglanishMalumoti.id == id))
        boglanish = result.scalar_one_or_none()
        if not boglanish:
            raise HTTPException(
                status_code=404, detail="Bog'lanish ma'lumoti topilmadi")

        if boglanish_data.joylashuv:
            boglanish.joylashuv = boglanish_data.joylashuv
        if boglanish_data.manzil:
            boglanish.manzil = boglanish_data.manzil
        if boglanish_data.email:
            boglanish.email = boglanish_data.email
        if boglanish_data.qoshimcha_email:
            boglanish.qoshimcha_email = boglanish_data.qoshimcha_email
        if boglanish_data.tel_raqam:
            boglanish.tel_raqam = boglanish_data.tel_raqam

        await db.commit()
        await db.refresh(boglanish)
        return boglanish
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bog'lanish ma'lumoti yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(TmsitiBoglanishMalumoti).where(TmsitiBoglanishMalumoti.id == id))
        boglanish = result.scalar_one_or_none()
        if not boglanish:
            raise HTTPException(
                status_code=404, detail="Bog'lanish ma'lumoti topilmadi")

        await db.delete(boglanish)
        await db.commit()
        return {"message": "Bog'lanish ma'lumoti muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bog'lanish ma'lumoti o'chirishda xato yuz berdi: {str(e)}"
        )
