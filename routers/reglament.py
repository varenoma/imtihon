import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.reglament import Reglament
from schemas.reglament import ReglamentCreate, ReglamentUpdate, ReglamentOut, PaginatedReglamentOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv
from pydantic import HttpUrl

router = APIRouter(prefix="/reglamentlar", tags=["Reglamentlar"])

load_dotenv()

PDF_FOLDER = os.getenv("PDF_FOLDER", "static/pdfs")
ALLOWED_FILE_TYPES = ["application/pdf"]


def validate_url(value: str | None) -> str | None:
    """URL ni validatsiya qilish funksiyasi. Agar qiymat kiritilgan bo'lsa, u to'g'ri URL bo'lishi kerak."""
    if value:
        try:
            # HttpUrl orqali validatsiya
            result = HttpUrl(value)
            return str(result)  # HttpUrl ob'ektini str ga aylantirish
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Kiritilgan havola to'g'ri URL formatida bo'lishi kerak (masalan, 'https://example.com')."
            )
    return value


@router.get("/", response_model=PaginatedReglamentOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(Reglament))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(Reglament).offset(offset).limit(
                per_page).order_by(Reglament.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedReglamentOut(
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


@router.post("/for_admin/", response_model=ReglamentOut)
async def create(
    shifri: str = Form(..., min_length=1, max_length=100,
                       description="Reglament shifri"),
    nomi: str = Form(..., min_length=1, max_length=255,
                     description="Reglament nomi"),
    link: str = Form(
        None, description="Tashqi havola (ixtiyoriy, lekin kiritilgan bo'lsa, to'g'ri URL bo'lishi kerak)"),
    pdf: UploadFile = File(
        None, description="PDF fayl (ixtiyoriy, faqat PDF formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # Linkni validatsiya qilish
        validated_link = validate_url(link)

        # ReglamentCreate schemaga ma'lumotlarni yuborish
        reglament_data = ReglamentCreate(
            shifri=shifri,
            nomi=nomi,
            link=validated_link,
            pdf=None
        )

        file_path = None
        if pdf:
            if pdf.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Yaroqsiz fayl turi: {pdf.content_type}. Faqat PDF fayllar ruxsat etiladi."
                )

            os.makedirs(PDF_FOLDER, exist_ok=True)
            filename = f"{uuid4().hex}_{pdf.filename}"
            file_path = os.path.join(PDF_FOLDER, filename)

            async with aio_open(file_path, "wb") as f:
                await f.write(await pdf.read())

        new_reglament = Reglament(
            shifri=reglament_data.shifri,
            nomi=reglament_data.nomi,
            link=reglament_data.link,
            pdf=file_path
        )
        db.add(new_reglament)
        await db.commit()
        await db.refresh(new_reglament)
        return new_reglament
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reglament yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=ReglamentOut)
async def update(
    id: int,
    shifri: str = Form(None, min_length=1, max_length=100,
                       description="Reglament shifri (ixtiyoriy)"),
    nomi: str = Form(None, min_length=1, max_length=255,
                     description="Reglament nomi (ixtiyoriy)"),
    link: str = Form(
        None, description="Tashqi havola (ixtiyoriy, lekin kiritilgan bo'lsa, to'g'ri URL bo'lishi kerak)"),
    pdf: UploadFile = File(
        None, description="PDF fayl (ixtiyoriy, faqat PDF formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # Linkni validatsiya qilish
        validated_link = validate_url(link)

        # ReglamentUpdate schemaga ma'lumotlarni yuborish
        reglament_data = ReglamentUpdate(
            shifri=shifri,
            nomi=nomi,
            link=validated_link,
            pdf=None
        )

        result = await db.execute(select(Reglament).where(Reglament.id == id))
        reglament = result.scalar_one_or_none()
        if not reglament:
            raise HTTPException(status_code=404, detail="Reglament topilmadi")

        if pdf:
            if pdf.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Yaroqsiz fayl turi: {pdf.content_type}. Faqat PDF fayllar ruxsat etiladi."
                )

            if reglament.pdf and os.path.exists(reglament.pdf):
                os.remove(reglament.pdf)

            filename = f"{uuid4().hex}_{pdf.filename}"
            file_path = os.path.join(PDF_FOLDER, filename)
            async with aio_open(file_path, "wb") as f:
                await f.write(await pdf.read())
            reglament.pdf = file_path
        elif pdf is None and reglament_data.pdf is None and reglament.pdf:
            # Agar PDF yuklanmasa va eski PDF bo'lsa, uni o'chirish
            if os.path.exists(reglament.pdf):
                os.remove(reglament.pdf)
            reglament.pdf = None

        if reglament_data.shifri:
            reglament.shifri = reglament_data.shifri
        if reglament_data.nomi:
            reglament.nomi = reglament_data.nomi
        if reglament_data.link is not None:
            reglament.link = reglament_data.link

        await db.commit()
        await db.refresh(reglament)
        return reglament
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reglament yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(Reglament).where(Reglament.id == id))
        reglament = result.scalar_one_or_none()
        if not reglament:
            raise HTTPException(status_code=404, detail="Reglament topilmadi")

        if reglament.pdf and os.path.exists(reglament.pdf):
            os.remove(reglament.pdf)

        await db.delete(reglament)
        await db.commit()
        return {"message": "Reglament muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reglament o'chirishda xato yuz berdi: {str(e)}"
        )
