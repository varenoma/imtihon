import os
import re
from uuid import uuid4
from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.guruh import Guruh
from models.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolim
from schemas.guruh import GuruhOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator, HttpUrl

router = APIRouter(prefix="/guruhlar", tags=["Guruhlar"])

load_dotenv()

PDF_FOLDER = os.getenv("PDF_FOLDER", "static/pdfs")
ALLOWED_FILE_TYPES = ["application/pdf"]


class GuruhCreate(BaseModel):
    shifr: str = Field(..., min_length=3,
                       description="Shifr, kamida 3 belgi. Masalan: 'ABC-123'")
    hujjat_nomi: str = Field(..., min_length=5,
                             description="Hujjat nomi, kamida 5 belgi. Masalan: 'Shaharsozlik qoidasi'")
    link: str | None = Field(
        None, description="Hujjat linki, to'g'ri URL formati. Masalan: 'https://example.com'")
    pdf: str | None = Field(
        None, description="PDF fayl yo'li. Masalan: '/static/pdfs/document.pdf'")
    bolim: int = Field(...,
                       description="Shaharsozlik norma qoida bo'limi ID'si. Masalan: 1")

    @validator("shifr")
    def validate_shifr(cls, v):
        return v.strip()

    @validator("hujjat_nomi")
    def validate_hujjat_nomi(cls, v):
        return v.strip()

    @validator("link")
    def validate_link(cls, v):
        if v and not re.match(r"^https?://", v):
            raise ValueError(
                "Link to'g'ri URL bo'lishi kerak. Masalan: 'https://example.com'")
        return v


@router.get(
    "/",
    response_model=list[GuruhOut],
    summary="Barcha guruhlarni olish",
    description="Barcha guruhlarni yoki ma'lum bir bo'limga tegishli guruhlarni sahifalarga bo'lib olish. Limit, offset va ixtiyoriy bo'lim parametri yordamida so'rovni boshqarish mumkin. Har bir guruh bo'lim ma'lumotlari bilan qaytariladi.",
    response_description="Guruhlar ro'yxati, har birida id, shifr, hujjat nomi, link, PDF yo'li va bo'lim ma'lumotlari."
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(
        10, ge=1, le=100, description="Bir sahifadagi guruhlar soni (1-100). Masalan: 10"),
    offset: int = Query(
        0, ge=0, description="Qaysi yozuvdan boshlash (0 yoki undan katta). Masalan: 0"),
    bolim: int | None = Query(
        None, description="Bo'lim ID'si bo'yicha filtr. Masalan: 1. Agar berilmasa, barcha guruhlar qaytariladi.")
):
    try:
        # Bo'lim mavjudligini tekshirish, agar berilgan bo'lsa
        if bolim is not None:
            result = await db.execute(select(ShaharsozlikNormaQoidaBolim).where(ShaharsozlikNormaQoidaBolim.id == bolim))
            bolim_obj = result.scalar_one_or_none()
            if not bolim_obj:
                raise HTTPException(
                    status_code=404, detail=f"Bo'lim ID'si {bolim} topilmadi")

        # Guruhlar so'rovi
        query = select(Guruh).options(joinedload(Guruh.bolim_obj)).offset(
            offset).limit(limit).order_by(Guruh.id)
        if bolim is not None:
            query = query.where(Guruh.bolim == bolim)

        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni olishda xato: {str(e)}")


@router.post(
    "/for_admin/",
    response_model=GuruhOut,
    summary="Yangi guruh yaratish",
    description="Faqat adminlar uchun: Yangi guruh yaratish. Shifr (kamida 3 belgi), hujjat_nomi (kamida 5 belgi), va bo'lim (mavjud bo'lim ID'si) majburiy. Link va PDF ixtiyoriy, PDF faqat 'application/pdf' bo'lishi kerak.",
    response_description="Yaratilgan guruh ma'lumotlari."
)
async def create_guruh(
    shifr: str = Form(...,
                      description="Shifr, kamida 3 belgi. Masalan: 'ABC-123'"),
    hujjat_nomi: str = Form(
        ..., description="Hujjat nomi, kamida 5 belgi. Masalan: 'Shaharsozlik qoidasi'"),
    link: str = Form(
        None, description="Hujjat linki, to'g'ri URL formati. Masalan: 'https://example.com'"),
    pdf: UploadFile = File(
        None, description="PDF fayl, faqat 'application/pdf'. Masalan: document.pdf"),
    bolim: int = Form(..., description="Bo'lim ID'si. Masalan: 1"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = GuruhCreate(
            shifr=shifr, hujjat_nomi=hujjat_nomi, link=link, bolim=bolim)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Bo'lim mavjudligini tekshirish
    result = await db.execute(select(ShaharsozlikNormaQoidaBolim).where(ShaharsozlikNormaQoidaBolim.id == bolim))
    bolim_obj = result.scalar_one_or_none()
    if not bolim_obj:
        raise HTTPException(status_code=404, detail="Bo'lim topilmadi")

    # PDF yuklash
    pdf_url = None  # Sukut qiymat sifatida None
    if pdf:
        if pdf.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Faqat PDF fayllar ruxsat etiladi (application/pdf). Masalan: document.pdf"
            )
        filename = f"{uuid4().hex}_{pdf.filename}"
        file_path = os.path.join(PDF_FOLDER, filename)
        os.makedirs(PDF_FOLDER, exist_ok=True)
        try:
            async with aio_open(file_path, "wb") as f:
                await f.write(await pdf.read())
            pdf_url = f"/static/pdfs/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"PDFni saqlashda xato: {str(e)}")

    new_guruh = Guruh(
        shifr=data.shifr,
        hujjat_nomi=data.hujjat_nomi,
        link=data.link,
        pdf=pdf_url,
        bolim=bolim
    )
    try:
        db.add(new_guruh)
        await db.commit()
        await db.refresh(new_guruh)
        # Explicitly load bolim_obj after refresh
        result = await db.execute(
            select(Guruh)
            .options(joinedload(Guruh.bolim_obj))
            .where(Guruh.id == new_guruh.id)
        )
        new_guruh = result.scalar_one()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni saqlashda xato: {str(e)}")
    return new_guruh


@router.put(
    "/{id}/for_admin/",
    response_model=GuruhOut,
    summary="Guruhni yangilash",
    description="Faqat adminlar uchun: Mavjud guruhni yangilash. ID orqali guruh topiladi va yangi ma'lumotlar (shifr, hujjat_nomi, link, pdf, bolim) bilan yangilanadi.",
    response_description="Yangilangan guruh ma'lumotlari."
)
async def update_guruh(
    id: int,
    shifr: str = Form(...,
                      description="Shifr, kamida 3 belgi. Masalan: 'ABC-123'"),
    hujjat_nomi: str = Form(
        ..., description="Hujjat nomi, kamida 5 belgi. Masalan: 'Shaharsozlik qoidasi'"),
    link: str = Form(
        None, description="Hujjat linki, to'g'ri URL formati. Masalan: 'https://example.com'"),
    pdf: UploadFile = File(
        None, description="PDF fayl, faqat 'application/pdf'. Masalan: document.pdf"),
    bolim: int = Form(..., description="Bo'lim ID'si. Masalan: 1"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = GuruhCreate(
            shifr=shifr, hujjat_nomi=hujjat_nomi, link=link, bolim=bolim)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Guruhni topish
    result = await db.execute(select(Guruh).where(Guruh.id == id))
    guruh = result.scalar_one_or_none()
    if not guruh:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    # Bo'lim mavjudligini tekshirish
    result = await db.execute(select(ShaharsozlikNormaQoidaBolim).where(ShaharsozlikNormaQoidaBolim.id == bolim))
    bolim_obj = result.scalar_one_or_none()
    if not bolim_obj:
        raise HTTPException(status_code=404, detail="Bo'lim topilmadi")

    # PDF yangilash
    if pdf:
        if pdf.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Faqat PDF fayllar ruxsat etiladi (application/pdf). Masalan: document.pdf"
            )
        old_path = guruh.pdf.lstrip("/") if guruh.pdf else None
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Eski PDFni o'chirishda xato: {str(e)}")

        filename = f"{uuid4().hex}_{pdf.filename}"
        file_path = os.path.join(PDF_FOLDER, filename)
        os.makedirs(PDF_FOLDER, exist_ok=True)
        try:
            async with aio_open(file_path, "wb") as f:
                await f.write(await pdf.read())
            guruh.pdf = f"/static/pdfs/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"PDFni saqlashda xato: {str(e)}")
    else:
        # Agar PDF kiritilmasa, pdf maydoni NULL qilinadi
        old_path = guruh.pdf.lstrip("/") if guruh.pdf else None
        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Eski PDFni o'chirishda xato: {str(e)}")
        guruh.pdf = None

    guruh.shifr = data.shifr
    guruh.hujjat_nomi = data.hujjat_nomi
    guruh.link = data.link
    guruh.bolim = bolim

    try:
        await db.commit()
        await db.refresh(guruh)
        # Explicitly load bolim_obj after refresh
        result = await db.execute(
            select(Guruh)
            .options(joinedload(Guruh.bolim_obj))
            .where(Guruh.id == guruh.id)
        )
        guruh = result.scalar_one()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni yangilashda xato: {str(e)}")
    return guruh


@router.delete(
    "/{id}/for_admin/",
    summary="Guruhni o'chirish",
    description="Faqat adminlar uchun: ID orqali guruhni o'chirish. Agar PDF fayl mavjud bo'lsa, u ham o'chiriladi.",
    response_description="O'chirish muvaffaqiyatli amalga oshirildi."
)
async def delete_guruh(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(Guruh).where(Guruh.id == id))
    guruh = result.scalar_one_or_none()
    if not guruh:
        raise HTTPException(status_code=404, detail="Guruh topilmadi")

    if guruh.pdf:
        old_path = guruh.pdf.lstrip("/")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"PDFni o'chirishda xato: {str(e)}")

    try:
        await db.delete(guruh)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
