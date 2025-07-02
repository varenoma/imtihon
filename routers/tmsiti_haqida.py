import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.tmsiti_haqida import TmsitiHaqida
from schemas.tmsiti_haqida import TmsitiHaqidaOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv

router = APIRouter(prefix="/tmsiti-haqida", tags=["Tmsiti Haqida"])

load_dotenv()

PDF_FOLDER = os.getenv("PDF_FOLDER")


@router.get("/", response_model=list[TmsitiHaqidaOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TmsitiHaqida))
    return result.scalars().all()


@router.post("/for_admin/", response_model=TmsitiHaqidaOut)
async def create(
    text: str = Form(...),
    pdf: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    allowed_types = ["application/pdf", "image/png", "image/jpeg"]
    if pdf.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Yaroqsiz fayl turi: {pdf.content_type}. Faqat PDF, PNG, JPG, JPEG ruxsat etiladi"
        )

    filename = f"{uuid4().hex}_{pdf.filename}"
    path = os.path.join(PDF_FOLDER, filename)

    async with aio_open(path, "wb") as f:
        await f.write(await pdf.read())

    new = TmsitiHaqida(text=text, pdf=f"/static/pdfs/{filename}")
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


@router.put("/{id}/for_admin/", response_model=TmsitiHaqidaOut)
async def update(
    id: int,
    text: str = Form(...),
    pdf: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(TmsitiHaqida).where(TmsitiHaqida.id == id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, detail="Topilmadi")

    if pdf:
        allowed_types = ["application/pdf", "image/png", "image/jpeg"]
        if pdf.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {pdf.content_type}. Faqat PDF, PNG, JPG, JPEG ruxsat etiladi"
            )

        old_path = row.pdf.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

        filename = f"{uuid4().hex}_{pdf.filename}"
        path = os.path.join(PDF_FOLDER, filename)
        async with aio_open(path, "wb") as f:
            await f.write(await pdf.read())
        row.pdf = f"/static/pdfs/{filename}"

    row.text = text
    await db.commit()
    await db.refresh(row)
    return row


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(TmsitiHaqida).where(TmsitiHaqida.id == id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, detail="Topilmadi")

    if row.pdf:
        path = row.pdf.lstrip("/")
        if os.path.exists(path):
            os.remove(path)

    await db.delete(row)
    await db.commit()
    return {"message": "O'chirildi"}
