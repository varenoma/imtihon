from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.corrupsiyaga_qarshi import Corrupsiya
from schemas.corrupsiya import CorrupsiyaCreate, CorrupsiyaUpdate, CorrupsiyaOut, PaginatedCorrupsiyaOut
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/corrupsiyaga_qarshi", tags=["Korrupsiyaga qarshi"])


@router.get("/", response_model=PaginatedCorrupsiyaOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(Corrupsiya))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(Corrupsiya).offset(offset).limit(
                per_page).order_by(Corrupsiya.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedCorrupsiyaOut(
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


@router.post("/for_admin/", response_model=CorrupsiyaOut)
async def create(
    name: str = Form(..., description="Korrupsiyaga qarshi yozuvning nomi"),
    description: str = Form(...,
                            description="Korrupsiyaga qarshi yozuvning tavsifi"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # CorrupsiyaCreate schemaga ma'lumotlarni yuborish
        corrupsiya_data = CorrupsiyaCreate(
            name=name,
            description=description
        )

        new_corrupsiya = Corrupsiya(
            name=corrupsiya_data.name,
            description=corrupsiya_data.description
        )
        db.add(new_corrupsiya)
        await db.commit()
        await db.refresh(new_corrupsiya)
        return new_corrupsiya
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yozuv yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=CorrupsiyaOut)
async def update(
    id: int,
    name: str = Form(
        None, description="Korrupsiyaga qarshi yozuvning nomi (ixtiyoriy)"),
    description: str = Form(
        None, description="Korrupsiyaga qarshi yozuvning tavsifi (ixtiyoriy)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # CorrupsiyaUpdate schemaga ma'lumotlarni yuborish
        corrupsiya_data = CorrupsiyaUpdate(
            name=name,
            description=description
        )

        result = await db.execute(select(Corrupsiya).where(Corrupsiya.id == id))
        corrupsiya = result.scalar_one_or_none()
        if not corrupsiya:
            raise HTTPException(status_code=404, detail="Yozuv topilmadi")

        if corrupsiya_data.name:
            corrupsiya.name = corrupsiya_data.name
        if corrupsiya_data.description:
            corrupsiya.description = corrupsiya_data.description

        await db.commit()
        await db.refresh(corrupsiya)
        return corrupsiya
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yozuv yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(Corrupsiya).where(Corrupsiya.id == id))
        corrupsiya = result.scalar_one_or_none()
        if not corrupsiya:
            raise HTTPException(status_code=404, detail="Yozuv topilmadi")

        await db.delete(corrupsiya)
        await db.commit()
        return {"message": "Yozuv muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yozuv o'chirishda xato yuz berdi: {str(e)}"
        )
