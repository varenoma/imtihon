import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.standart import Standart
from schemas.standart import StandartCreate, StandartUpdate, StandartOut, PaginatedStandartOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv

router = APIRouter(prefix="/standartlar", tags=["Standartlar"])

load_dotenv()

PDF_FOLDER = os.getenv("PDF_FOLDER", "static/pdfs")
ALLOWED_FILE_TYPES = ["application/pdf"]


@router.get("/", response_model=PaginatedStandartOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Sahifa raqami"),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni")
):
    # Umumiy elementlar sonini hisoblash
    total_query = await db.execute(select(func.count()).select_from(Standart))
    total = total_query.scalar()

    # Sahifalash uchun ma'lumotlarni olish
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Standart).offset(offset).limit(per_page).order_by(Standart.id)
    )
    items = result.scalars().all()

    # Umumiy sahifalar sonini hisoblash
    total_pages = (total + per_page - 1) // per_page

    return PaginatedStandartOut(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/for_admin/", response_model=StandartOut)
async def create(
    name: str = Form(..., min_length=1, max_length=255),
    description: str = Form(None),
    pdf: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    if pdf.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Yaroqsiz fayl turi: {pdf.content_type}. Faqat PDF ruxsat etiladi"
        )

    os.makedirs(PDF_FOLDER, exist_ok=True)
    filename = f"{uuid4().hex}_{pdf.filename}"
    file_path = os.path.join(PDF_FOLDER, filename)

    async with aio_open(file_path, "wb") as f:
        await f.write(await pdf.read())

    new_standart = Standart(
        name=name,
        description=description,
        pdf=file_path
    )
    db.add(new_standart)
    await db.commit()
    await db.refresh(new_standart)
    return new_standart


@router.put("/{id}/for_admin/", response_model=StandartOut)
async def update(
    id: int,
    name: str = Form(None, min_length=1, max_length=255),
    description: str = Form(None),
    pdf: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(Standart).where(Standart.id == id))
    standart = result.scalar_one_or_none()
    if not standart:
        raise HTTPException(404, detail="Standart topilmadi")

    if pdf:
        if pdf.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {pdf.content_type}. Faqat PDF ruxsat etiladi"
            )

        if standart.pdf and os.path.exists(standart.pdf):
            os.remove(standart.pdf)

        filename = f"{uuid4().hex}_{pdf.filename}"
        file_path = os.path.join(PDF_FOLDER, filename)
        async with aio_open(file_path, "wb") as f:
            await f.write(await pdf.read())
        standart.pdf = file_path

    if name:
        standart.name = name
    if description is not None:
        standart.description = description

    await db.commit()
    await db.refresh(standart)
    return standart


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(Standart).where(Standart.id == id))
    standart = result.scalar_one_or_none()
    if not standart:
        raise HTTPException(404, detail="Standart topilmadi")

    if standart.pdf and os.path.exists(standart.pdf):
        os.remove(standart.pdf)

    await db.delete(standart)
    await db.commit()
    return {"message": "Standart o'chirildi"}
