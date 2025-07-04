import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.malumotnoma import Malumotnoma
from schemas.malumotnoma import MalumotnomaCreate, MalumotnomaUpdate, MalumotnomaOut, PaginatedMalumotnomaOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv

router = APIRouter(prefix="/malumotnoma", tags=["Ma'lumotnomalar"])

load_dotenv()

PDF_FOLDER = os.getenv("PDF_FOLDER", "static/pdfs")
ALLOWED_FILE_TYPES = ["application/pdf"]


@router.get("/", response_model=PaginatedMalumotnomaOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(Malumotnoma))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(Malumotnoma).offset(offset).limit(
                per_page).order_by(Malumotnoma.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedMalumotnomaOut(
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


@router.post("/for_admin/", response_model=MalumotnomaOut)
async def create(
    nomi: str = Form(..., description="Ma'lumotnoma nomi"),
    hujjat: UploadFile = File(...,
                              description="PDF fayl (majburiy, faqat PDF formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        if hujjat.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {hujjat.content_type}. Faqat PDF fayllar ruxsat etiladi."
            )

        os.makedirs(PDF_FOLDER, exist_ok=True)
        filename = f"{uuid4().hex}_{hujjat.filename}"
        file_path = os.path.join(PDF_FOLDER, filename)

        async with aio_open(file_path, "wb") as f:
            await f.write(await hujjat.read())

        # MalumotnomaCreate schemaga ma'lumotlarni yuborish
        malumotnoma_data = MalumotnomaCreate(
            nomi=nomi,
            hujjat=file_path
        )

        new_malumotnoma = Malumotnoma(
            nomi=malumotnoma_data.nomi,
            hujjat=malumotnoma_data.hujjat
        )
        db.add(new_malumotnoma)
        await db.commit()
        await db.refresh(new_malumotnoma)
        return new_malumotnoma
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ma'lumotnoma yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=MalumotnomaOut)
async def update(
    id: int,
    nomi: str = Form(None, description="Ma'lumotnoma nomi (ixtiyoriy)"),
    hujjat: UploadFile = File(
        None, description="PDF fayl (ixtiyoriy, faqat PDF formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # MalumotnomaUpdate schemaga ma'lumotlarni yuborish
        malumotnoma_data = MalumotnomaUpdate(
            nomi=nomi,
            hujjat=None
        )

        result = await db.execute(select(Malumotnoma).where(Malumotnoma.id == id))
        malumotnoma = result.scalar_one_or_none()
        if not malumotnoma:
            raise HTTPException(
                status_code=404, detail="Ma'lumotnoma topilmadi")

        if hujjat:
            if hujjat.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Yaroqsiz fayl turi: {hujjat.content_type}. Faqat PDF fayllar ruxsat etiladi."
                )

            if malumotnoma.hujjat and os.path.exists(malumotnoma.hujjat):
                os.remove(malumotnoma.hujjat)

            filename = f"{uuid4().hex}_{hujjat.filename}"
            file_path = os.path.join(PDF_FOLDER, filename)
            async with aio_open(file_path, "wb") as f:
                await f.write(await hujjat.read())
            malumotnoma.hujjat = file_path

        if malumotnoma_data.nomi:
            malumotnoma.nomi = malumotnoma_data.nomi

        await db.commit()
        await db.refresh(malumotnoma)
        return malumotnoma
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ma'lumotnoma yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(Malumotnoma).where(Malumotnoma.id == id))
        malumotnoma = result.scalar_one_or_none()
        if not malumotnoma:
            raise HTTPException(
                status_code=404, detail="Ma'lumotnoma topilmadi")

        if malumotnoma.hujjat and os.path.exists(malumotnoma.hujjat):
            os.remove(malumotnoma.hujjat)

        await db.delete(malumotnoma)
        await db.commit()
        return {"message": "Ma'lumotnoma muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ma'lumotnoma o'chirishda xato yuz berdi: {str(e)}"
        )
