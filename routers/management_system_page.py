from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.management_system_page import ManagementSystemPage
from schemas.management_system_page import ManagementSystemPageCreate, ManagementSystemPageUpdate, ManagementSystemPageOut, PaginatedManagementSystemPageOut
from auth.dependencies import get_current_admin

router = APIRouter(prefix="/management_system_page",
                   tags=["Boshqaruv Tizimi Sahifalari"])


@router.get("/", response_model=PaginatedManagementSystemPageOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(ManagementSystemPage))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(ManagementSystemPage).offset(offset).limit(
                per_page).order_by(ManagementSystemPage.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedManagementSystemPageOut(
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


@router.post("/for_admin/", response_model=ManagementSystemPageOut)
async def create(
    page: str = Form(..., description="Boshqaruv tizimi sahifasining matni"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # ManagementSystemPageCreate schemaga ma'lumotlarni yuborish
        page_data = ManagementSystemPageCreate(
            page=page
        )

        new_page = ManagementSystemPage(
            page=page_data.page
        )
        db.add(new_page)
        await db.commit()
        await db.refresh(new_page)
        return new_page
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sahifa yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=ManagementSystemPageOut)
async def update(
    id: int,
    page: str = Form(
        None, description="Boshqaruv tizimi sahifasining matni (ixtiyoriy)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # ManagementSystemPageUpdate schemaga ma'lumotlarni yuborish
        page_data = ManagementSystemPageUpdate(
            page=page
        )

        result = await db.execute(select(ManagementSystemPage).where(ManagementSystemPage.id == id))
        existing_page = result.scalar_one_or_none()
        if not existing_page:
            raise HTTPException(status_code=404, detail="Sahifa topilmadi")

        if page_data.page:
            existing_page.page = page_data.page

        await db.commit()
        await db.refresh(existing_page)
        return existing_page
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sahifa yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(ManagementSystemPage).where(ManagementSystemPage.id == id))
        page = result.scalar_one_or_none()
        if not page:
            raise HTTPException(status_code=404, detail="Sahifa topilmadi")

        await db.delete(page)
        await db.commit()
        return {"message": "Sahifa muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sahifa o'chirishda xato yuz berdi: {str(e)}"
        )
