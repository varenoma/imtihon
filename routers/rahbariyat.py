from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.rahbariyat import Rahbariyat
from core.database import get_db
from auth.dependencies import get_current_admin
from dotenv import load_dotenv
from aiofiles import open as aio_open
from schemas.rahbariyat import RahbariyatOut
import os
from uuid import uuid4

router = APIRouter(prefix="/rahbariyat", tags=["Rahbariyat"])

load_dotenv()

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "static/images")
ALLOWED_IMAGE_TYPES = os.getenv(
    "ALLOWED_IMAGE_TYPES", "image/png,image/jpeg,image/jpg").split(",")


@router.get("/", response_model=list[RahbariyatOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rahbariyat))
    return result.scalars().all()


@router.post("/for_admin/", response_model=RahbariyatOut)
async def create_rahbariyat(
    positions: str = Form(...),
    full_name: str = Form(...),
    qabul_kunlari: str = Form(...),
    telefon: str = Form(...),
    elektron_pochta: str = Form(...),
    mutahassisligi: str = Form(...),
    rasm: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    if rasm:
        if rasm.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                400, detail="Faqat PNG, JPG, JPEG ruxsat etiladi.")
        filename = f"{uuid4().hex}_{rasm.filename}"
        file_path = os.path.join(IMAGE_FOLDER, filename)
        async with aio_open(file_path, "wb") as f:
            await f.write(await rasm.read())
        image_url = f"/static/images/{filename}"
    else:
        image_url = "/static/images/default.png"

    new_person = Rahbariyat(
        positions=positions,
        full_name=full_name,
        qabul_kunlari=qabul_kunlari,
        telefon=telefon,
        elektron_pochta=elektron_pochta,
        mutahassisligi=mutahassisligi,
        rasm=image_url
    )
    db.add(new_person)
    await db.commit()
    await db.refresh(new_person)
    return new_person


@router.put("/{id}/for_admin/", response_model=RahbariyatOut)
async def update_rahbariyat(
    id: int,
    positions: str = Form(...),
    full_name: str = Form(...),
    qabul_kunlari: str = Form(...),
    telefon: str = Form(...),
    elektron_pochta: str = Form(...),
    mutahassisligi: str = Form(...),
    rasm: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(Rahbariyat).where(Rahbariyat.id == id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(404, detail="Topilmadi")

    if rasm:
        if rasm.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                400, detail="Faqat PNG, JPG, JPEG ruxsat etiladi.")

        old_path = person.rasm.lstrip("/")
        if os.path.exists(old_path) and "default.png" not in old_path:
            os.remove(old_path)

        filename = f"{uuid4().hex}_{rasm.filename}"
        file_path = os.path.join(IMAGE_FOLDER, filename)
        async with aio_open(file_path, "wb") as f:
            await f.write(await rasm.read())
        person.rasm = f"/static/images/{filename}"

    person.positions = positions
    person.full_name = full_name
    person.qabul_kunlari = qabul_kunlari
    person.telefon = telefon
    person.elektron_pochta = elektron_pochta
    person.mutahassisligi = mutahassisligi

    await db.commit()
    await db.refresh(person)
    return person


@router.delete("/{id}/for_admin/")
async def delete_rahbariyat(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(Rahbariyat).where(Rahbariyat.id == id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(404, detail="Topilmadi")

    if person.rasm and "default.png" not in person.rasm:
        old_path = person.rasm.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    await db.delete(person)
    await db.commit()
    return {"message": "O'chirildi"}
