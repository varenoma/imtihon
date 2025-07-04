import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from core.database import get_db
from models.smeta_resurs_norma import SmetaResursNorma
from schemas.smeta_resurs_norma import SmetaResursNormaCreate, SmetaResursNormaUpdate, SmetaResursNormaOut, PaginatedSmetaResursNormaOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv

router = APIRouter(prefix="/smeta_resurs_normalari",
                   tags=["Smeta Resurs Normalari"])

load_dotenv()

PDF_FOLDER = os.getenv("PDF_FOLDER", "static/pdfs")
ALLOWED_FILE_TYPES = ["application/pdf"]


@router.get("/", response_model=PaginatedSmetaResursNormaOut)
async def get_all(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1, ge=1, description="Sahifa raqami, 1 dan kam bo'lmasligi kerak."),
    per_page: int = Query(
        10, ge=1, le=100, description="Har bir sahifadagi elementlar soni, 1-100 oralig'ida.")
):
    try:
        # Umumiy elementlar sonini hisoblash
        total_query = await db.execute(select(func.count()).select_from(SmetaResursNorma))
        total = total_query.scalar()

        # Sahifalash uchun ma'lumotlarni olish
        offset = (page - 1) * per_page
        result = await db.execute(
            select(SmetaResursNorma).offset(offset).limit(
                per_page).order_by(SmetaResursNorma.id)
        )
        items = result.scalars().all()

        # Umumiy sahifalar sonini hisoblash
        total_pages = (total + per_page - 1) // per_page

        return PaginatedSmetaResursNormaOut(
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


@router.post("/for_admin/", response_model=SmetaResursNormaOut)
async def create(
    yangi_ShNQ_raqami: str = Form(..., description="Yangi ShNQ raqami"),
    yangilangan_ShNQ_nomi: str = Form(...,
                                      description="Yangilangan ShNQ nomi"),
    ShNQ_raqami: str = Form(..., description="ShNQ raqami"),
    ShNQ_nomi: str = Form(..., description="ShNQ nomi"),
    pdf: UploadFile = File(
        None, description="PDF fayl (ixtiyoriy, faqat PDF formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # SmetaResursNormaCreate schemaga ma'lumotlarni yuborish
        smeta_data = SmetaResursNormaCreate(
            yangi_ShNQ_raqami=yangi_ShNQ_raqami,
            yangilangan_ShNQ_nomi=yangilangan_ShNQ_nomi,
            ShNQ_raqami=ShNQ_raqami,
            ShNQ_nomi=ShNQ_nomi,
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

        new_smeta = SmetaResursNorma(
            yangi_ShNQ_raqami=smeta_data.yangi_ShNQ_raqami,
            yangilangan_ShNQ_nomi=smeta_data.yangilangan_ShNQ_nomi,
            ShNQ_raqami=smeta_data.ShNQ_raqami,
            ShNQ_nomi=smeta_data.ShNQ_nomi,
            pdf=file_path
        )
        db.add(new_smeta)
        await db.commit()
        await db.refresh(new_smeta)
        return new_smeta
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Smeta resurs normasi yaratishda xato yuz berdi: {str(e)}"
        )


@router.put("/{id}/for_admin/", response_model=SmetaResursNormaOut)
async def update(
    id: int,
    yangi_ShNQ_raqami: str = Form(
        None, description="Yangi ShNQ raqami (ixtiyoriy)"),
    yangilangan_ShNQ_nomi: str = Form(
        None, description="Yangilangan ShNQ nomi (ixtiyoriy)"),
    ShNQ_raqami: str = Form(None, description="ShNQ raqami (ixtiyoriy)"),
    ShNQ_nomi: str = Form(None, description="ShNQ nomi (ixtiyoriy)"),
    pdf: UploadFile = File(
        None, description="PDF fayl (ixtiyoriy, faqat PDF formatida)"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        # SmetaResursNormaUpdate schemaga ma'lumotlarni yuborish
        smeta_data = SmetaResursNormaUpdate(
            yangi_ShNQ_raqami=yangi_ShNQ_raqami,
            yangilangan_ShNQ_nomi=yangilangan_ShNQ_nomi,
            ShNQ_raqami=ShNQ_raqami,
            ShNQ_nomi=ShNQ_nomi,
            pdf=None
        )

        result = await db.execute(select(SmetaResursNorma).where(SmetaResursNorma.id == id))
        smeta = result.scalar_one_or_none()
        if not smeta:
            raise HTTPException(
                status_code=404, detail="Smeta resurs normasi topilmadi")

        if pdf:
            if pdf.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Yaroqsiz fayl turi: {pdf.content_type}. Faqat PDF fayllar ruxsat etiladi."
                )

            if smeta.pdf and os.path.exists(smeta.pdf):
                os.remove(smeta.pdf)

            filename = f"{uuid4().hex}_{pdf.filename}"
            file_path = os.path.join(PDF_FOLDER, filename)
            async with aio_open(file_path, "wb") as f:
                await f.write(await pdf.read())
            smeta.pdf = file_path
        elif pdf is None and smeta_data.pdf is None and smeta.pdf:
            # Agar PDF yuklanmasa va eski PDF bo'lsa, uni o'chirish
            if os.path.exists(smeta.pdf):
                os.remove(smeta.pdf)
            smeta.pdf = None

        if smeta_data.yangi_ShNQ_raqami:
            smeta.yangi_ShNQ_raqami = smeta_data.yangi_ShNQ_raqami
        if smeta_data.yangilangan_ShNQ_nomi:
            smeta.yangilangan_ShNQ_nomi = smeta_data.yangilangan_ShNQ_nomi
        if smeta_data.ShNQ_raqami:
            smeta.ShNQ_raqami = smeta_data.ShNQ_raqami
        if smeta_data.ShNQ_nomi:
            smeta.ShNQ_nomi = smeta_data.ShNQ_nomi

        await db.commit()
        await db.refresh(smeta)
        return smeta
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Smeta resurs normasi yangilashda xato yuz berdi: {str(e)}"
        )


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        result = await db.execute(select(SmetaResursNorma).where(SmetaResursNorma.id == id))
        smeta = result.scalar_one_or_none()
        if not smeta:
            raise HTTPException(
                status_code=404, detail="Smeta resurs normasi topilmadi")

        if smeta.pdf and os.path.exists(smeta.pdf):
            os.remove(smeta.pdf)

        await db.delete(smeta)
        await db.commit()
        return {"message": "Smeta resurs normasi muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Smeta resurs normasi o'chirishda xato yuz berdi: {str(e)}"
        )
