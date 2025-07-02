import os
import re
from uuid import uuid4
from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.rahbariyat import Rahbariyat
from schemas.rahbariyat import RahbariyatOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, validator

router = APIRouter(prefix="/rahbariyat", tags=["Rahbariyat"])

load_dotenv()

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "static/images")
ALLOWED_IMAGE_TYPES = os.getenv(
    "ALLOWED_IMAGE_TYPES", "image/png,image/jpeg,image/jpg").split(",")


class RahbariyatCreate(BaseModel):
    positions: str
    full_name: str
    qabul_kunlari: str
    telefon: str
    elektron_pochta: EmailStr
    mutahassisligi: str

    @validator("positions")
    def validate_positions(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "Lavozim kamida 3 belgidan iborat bo'lishi kerak. Masalan: 'Direktor'")
        return v.strip()

    @validator("full_name")
    def validate_full_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "To'liq ism kamida 3 belgidan iborat bo'lishi kerak. Masalan: 'Aliyev Valijon'")
        return v.strip()

    @validator("qabul_kunlari")
    def validate_qabul_kunlari(cls, v):
        if len(v.strip()) < 5:
            raise ValueError(
                "Qabul kunlari kamida 5 belgidan iborat bo'lishi kerak. Masalan: 'Dushanba-Juma'")
        return v.strip()

    @validator("telefon")
    def validate_telefon(cls, v):
        pattern = r"^\+998[0-9]{9}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Telefon raqami +998 bilan boshlanishi va 12 belgidan iborat bo'lishi kerak. Masalan: '+998901234567'")
        return v

    @validator("mutahassisligi")
    def validate_mutahassisligi(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "Mutaxassislik kamida 3 belgidan iborat bo'lishi kerak. Masalan: 'IT mutaxassisi'")
        return v.strip()

    @validator("elektron_pochta")
    def validate_elektron_pochta(cls, v):
        if not v:
            raise ValueError(
                "Elektron pochta bo'sh bo'lmasligi kerak. Masalan: 'example@domain.com'")
        return v


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
    try:
        data = RahbariyatCreate(
            positions=positions,
            full_name=full_name,
            qabul_kunlari=qabul_kunlari,
            telefon=telefon,
            elektron_pochta=elektron_pochta,
            mutahassisligi=mutahassisligi
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if rasm:
        if rasm.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {rasm.content_type}. Faqat PNG, JPG, JPEG ruxsat etiladi. Masalan: rasm.jpg"
            )
        filename = f"{uuid4().hex}_{rasm.filename}"
        file_path = os.path.join(IMAGE_FOLDER, filename)
        try:
            async with aio_open(file_path, "wb") as f:
                await f.write(await rasm.read())
            image_url = f"/static/images/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Rasmni saqlashda xato: {str(e)}")
    else:
        image_url = "/static/images/default.png"

    new_person = Rahbariyat(
        positions=data.positions,
        full_name=data.full_name,
        qabul_kunlari=data.qabul_kunlari,
        telefon=data.telefon,
        elektron_pochta=data.elektron_pochta,
        mutahassisligi=data.mutahassisligi,
        rasm=image_url
    )
    try:
        db.add(new_person)
        await db.commit()
        await db.refresh(new_person)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni saqlashda xato: {str(e)}")
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
    try:
        data = RahbariyatCreate(
            positions=positions,
            full_name=full_name,
            qabul_kunlari=qabul_kunlari,
            telefon=telefon,
            elektron_pochta=elektron_pochta,
            mutahassisligi=mutahassisligi
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = await db.execute(select(Rahbariyat).where(Rahbariyat.id == id))
    person = result.scalar_one_or_none()
    if not person:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    if rasm:
        if rasm.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {rasm.content_type}. Faqat PNG, JPG, JPEG ruxsat etiladi. Masalan: rasm.jpg"
            )
        old_path = person.rasm.lstrip("/")
        if os.path.exists(old_path) and "default.png" not in old_path:
            try:
                os.remove(old_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Eski rasmni o'chirishda xato: {str(e)}")

        filename = f"{uuid4().hex}_{rasm.filename}"
        file_path = os.path.join(IMAGE_FOLDER, filename)
        try:
            async with aio_open(file_path, "wb") as f:
                await f.write(await rasm.read())
            person.rasm = f"/static/images/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Rasmni saqlashda xato: {str(e)}")

    person.positions = data.positions
    person.full_name = data.full_name
    person.qabul_kunlari = data.qabul_kunlari
    person.telefon = data.telefon
    person.elektron_pochta = data.elektron_pochta
    person.mutahassisligi = data.mutahassisligi

    try:
        await db.commit()
        await db.refresh(person)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni yangilashda xato: {str(e)}")
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
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    if person.rasm and "default.png" not in person.rasm:
        old_path = person.rasm.lstrip("/")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Rasmni o'chirishda xato: {str(e)}")

    try:
        await db.delete(person)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
