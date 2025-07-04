import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.yangiliklar import Yangilik
from schemas.yangilik import YangilikCreate, YangilikUpdate, YangilikOut, PaginatedYangilikOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv

router = APIRouter(prefix="/yangiliklar", tags=["Yangiliklar"])

load_dotenv()

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "static/images")
ALLOWED_FILE_TYPES = ["image/jpeg", "image/png"]


@router.get("/", response_model=PaginatedYangilikOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(Yangilik))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(Yangilik).offset(offset).limit(
                per_page).order_by(Yangilik.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedYangilikOut(
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


@router.post("/for_admin/", response_model=YangilikOut)
async def create(
    name: str = Form(..., description="Yangilikning nomi"),
    text: str = Form(..., description="Yangilikning matni"),
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

        # YangilikCreate schemaga ma'lumotlarni yuborish
        yangilik_data = YangilikCreate(
            name=name,
            text=text,
            rasm=file_path
        )

        new_yangilik = Yangilik(
            name=yangilik_data.name,
            text=yangilik_data.text,
            rasm=yangilik_data.rasm
        )
        db.add(new_yangilik)
        await db.commit()
        await db.refresh(new_yangilik)
        return new_yangilik
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yangilik yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=YangilikOut)
async def update(
    id: int,
    name: str = Form(None, description="Yangilikning nomi (ixtiyoriy)"),
    text: str = Form(None, description="Yangilikning matni (ixtiyoriy)"),
    rasm: UploadFile = File(
        None, description="Rasm fayl (ixtiyoriy, faqat JPEG yoki PNG formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # YangilikUpdate schemaga ma'lumotlarni yuborish
        yangilik_data = YangilikUpdate(
            name=name,
            text=text,
            rasm=None
        )

        result = await db.execute(select(Yangilik).where(Yangilik.id == id))
        yangilik = result.scalar_one_or_none()
        if not yangilik:
            raise HTTPException(status_code=404, detail="Yangilik topilmadi")

        if rasm:
            if rasm.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Yaroqsiz fayl turi: {rasm.content_type}. Faqat JPEG yoki PNG fayllar ruxsat etiladi."
                )

            if yangilik.rasm and os.path.exists(yangilik.rasm):
                os.remove(yangilik.rasm)

            filename = f"{uuid4().hex}_{rasm.filename}"
            file_path = os.path.join(IMAGE_FOLDER, filename)
            async with aio_open(file_path, "wb") as f:
                await f.write(await rasm.read())
            yangilik.rasm = file_path

        if yangilik_data.name:
            yangilik.name = yangilik_data.name
        if yangilik_data.text:
            yangilik.text = yangilik_data.text

        await db.commit()
        await db.refresh(yangilik)
        return yangilik
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yangilik yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(Yangilik).where(Yangilik.id == id))
        yangilik = result.scalar_one_or_none()
        if not yangilik:
            raise HTTPException(status_code=404, detail="Yangilik topilmadi")

        if yangilik.rasm and os.path.exists(yangilik.rasm):
            os.remove(yangilik.rasm)

        await db.delete(yangilik)
        await db.commit()
        return {"message": "Yangilik muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yangilik o'chirishda xato yuz berdi: {str(e)}"
        )
