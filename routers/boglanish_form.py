import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from core.database import get_db
from models.boglanish_form import BoglanishForm
from schemas.boglanish_form import BoglanishFormCreate, BoglanishFormOut, PaginatedBoglanishFormOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/boglanish_form", tags=["Bog'lanish Formasi"])

load_dotenv()

FILE_FOLDER = os.getenv("FILE_FOLDER", "static/files")
ALLOWED_FILE_TYPES = ["application/pdf"]


@router.get("/for_admin/", response_model=PaginatedBoglanishFormOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida."),
    search: Optional[str] = Query(
        None, description="FIO, email, tel_raqam yoki type bo'yicha umumiy qidiruv."),
    email: Optional[str] = Query(
        None, description="Maxsus email bo'yicha filtr."),
    tel_raqam: Optional[str] = Query(
        None, description="Maxsus telefon raqami bo'yicha filtr."),
    type: Optional[str] = Query(
        None, description="Maxsus murojat turi bo'yicha filtr."),
    created_at_start: Optional[datetime] = Query(
        None, description="Yaratilgan vaqt boshlanishi (masalan, 2025-01-01T00:00:00)."),
    created_at_end: Optional[datetime] = Query(
        None, description="Yaratilgan vaqt tugashi (masalan, 2025-12-31T23:59:59).")
):
    try:
        query = select(BoglanishForm)

        # Filtrlash shartlari
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    BoglanishForm.FIO.ilike(search),
                    BoglanishForm.email.ilike(search),
                    BoglanishForm.tel_raqam.ilike(search),
                    BoglanishForm.type.ilike(search)
                )
            )
        if email:
            query = query.filter(BoglanishForm.email == email)
        if tel_raqam:
            query = query.filter(BoglanishForm.tel_raqam == tel_raqam)
        if type:
            query = query.filter(BoglanishForm.type == type)
        if created_at_start:
            query = query.filter(BoglanishForm.created_at >= created_at_start)
        if created_at_end:
            query = query.filter(BoglanishForm.created_at <= created_at_end)

        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            query.offset(offset).limit(per_page).order_by(BoglanishForm.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedBoglanishFormOut(
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


@router.post("/", response_model=BoglanishFormOut)
async def create(
    FIO: str = Form(..., description="Foydalanuvchining FIOsi"),
    email: str = Form(..., description="Foydalanuvchining email manzili"),
    tel_raqam: str = Form(..., description="Telefon raqami"),
    type: str = Form(..., description="Murojat turi"),
    murojat_matni: str = Form(..., description="Murojat matni"),
    fayl: UploadFile = File(
        None, description="Fayl (ixtiyoriy, faqat PDF formatida)"),
    db: AsyncSession = Depends(get_db)
):
    try:
        if fayl and fayl.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {fayl.content_type}. Faqat PDF fayllar ruxsat etiladi."
            )

        file_path = None
        if fayl:
            os.makedirs(FILE_FOLDER, exist_ok=True)
            filename = f"{uuid4().hex}_{fayl.filename}"
            file_path = os.path.join(FILE_FOLDER, filename)
            async with aio_open(file_path, "wb") as f:
                await f.write(await fayl.read())

        # BoglanishFormCreate schemaga ma'lumotlarni yuborish
        boglanish_data = BoglanishFormCreate(
            FIO=FIO,
            email=email,
            tel_raqam=tel_raqam,
            type=type,
            murojat_matni=murojat_matni,
            fayl=file_path
        )

        new_boglanish = BoglanishForm(
            FIO=boglanish_data.FIO,
            email=boglanish_data.email,
            tel_raqam=boglanish_data.tel_raqam,
            type=boglanish_data.type,
            murojat_matni=boglanish_data.murojat_matni,
            fayl=boglanish_data.fayl
        )
        db.add(new_boglanish)
        await db.commit()
        await db.refresh(new_boglanish)
        return new_boglanish
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Murojat yaratishda xato yuz berdi: {str(e)}"
        )
