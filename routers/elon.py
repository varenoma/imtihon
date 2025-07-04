import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.elonlar import Elon
from schemas.elon import ElonCreate, ElonUpdate, ElonOut, PaginatedElonOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv

router = APIRouter(prefix="/elonlar", tags=["E'lonlar"])

load_dotenv()

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "static/images")
ALLOWED_FILE_TYPES = ["image/jpeg", "image/png"]


@router.get("/", response_model=PaginatedElonOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(Elon))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(Elon).offset(offset).limit(per_page).order_by(Elon.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedElonOut(
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


@router.post("/for_admin/", response_model=ElonOut)
async def create(
    name: str = Form(..., description="E'lonning nomi"),
    description: str = Form(..., description="E'lonning tavsifi"),
    rasm: UploadFile = File(...,
                            description="Rasm fayl (majburiy, faqat JPEG yoki PNG formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        if rasm.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {rasm.content_type}. Faqat JPEG yoki PNG fayllar ruxsat etiladi."
            )

        os.makedirs(IMAGE_FOLDER, exist_ok=True)
        filename = f"{uuid4().hex}_{rasm.filename}"
        file_path = os.path.join(IMAGE_FOLDER, filename)

        async with aio_open(file_path, "wb") as f:
            await f.write(await rasm.read())

        # ElonCreate schemaga ma'lumotlarni yuborish
        elon_data = ElonCreate(
            name=name,
            description=description,
            rasm=file_path
        )

        new_elon = Elon(
            name=elon_data.name,
            description=elon_data.description,
            rasm=elon_data.rasm
        )
        db.add(new_elon)
        await db.commit()
        await db.refresh(new_elon)
        return new_elon
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"E'lon yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=ElonOut)
async def update(
    id: int,
    name: str = Form(None, description="E'lonning nomi (ixtiyoriy)"),
    description: str = Form(None, description="E'lonning tavsifi (ixtiyoriy)"),
    rasm: UploadFile = File(
        None, description="Rasm fayl (ixtiyoriy, faqat JPEG yoki PNG formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # ElonUpdate schemaga ma'lumotlarni yuborish
        elon_data = ElonUpdate(
            name=name,
            description=description,
            rasm=None
        )

        result = await db.execute(select(Elon).where(Elon.id == id))
        elon = result.scalar_one_or_none()
        if not elon:
            raise HTTPException(status_code=404, detail="E'lon topilmadi")

        if rasm:
            if rasm.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Yaroqsiz fayl turi: {rasm.content_type}. Faqat JPEG yoki PNG fayllar ruxsat etiladi."
                )

            if elon.rasm and os.path.exists(elon.rasm):
                os.remove(elon.rasm)

            filename = f"{uuid4().hex}_{rasm.filename}"
            file_path = os.path.join(IMAGE_FOLDER, filename)
            async with aio_open(file_path, "wb") as f:
                await f.write(await rasm.read())
            elon.rasm = file_path

        if elon_data.name:
            elon.name = elon_data.name
        if elon_data.description:
            elon.description = elon_data.description

        await db.commit()
        await db.refresh(elon)
        return elon
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"E'lon yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(Elon).where(Elon.id == id))
        elon = result.scalar_one_or_none()
        if not elon:
            raise HTTPException(status_code=404, detail="E'lon topilmadi")

        if elon.rasm and os.path.exists(elon.rasm):
            os.remove(elon.rasm)

        await db.delete(elon)
        await db.commit()
        return {"message": "E'lon muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"E'lon o'chirishda xato yuz berdi: {str(e)}"
        )
