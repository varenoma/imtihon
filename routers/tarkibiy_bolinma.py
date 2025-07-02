import os
import re
from uuid import uuid4
from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.tarkibiy_bolinmalar import TarkibiyBolinma
from schemas.tarkibiy_bolinma import TarkibiyBolinmaOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, validator

router = APIRouter(prefix="/tarkibiy-bolinmalar", tags=["Tarkibiy Bolinmalar"])

load_dotenv()

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "static/images")
ALLOWED_IMAGE_TYPES = os.getenv(
    "ALLOWED_IMAGE_TYPES", "image/png,image/jpeg,image/jpg").split(",")


class TarkibiyBolinmaCreate(BaseModel):
    kimligi: str
    full_name: str
    telefon: str
    elektron_pochta: EmailStr
    image: str | None = None

    @validator("kimligi")
    def validate_kimligi(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "Kimligi kamida 3 belgidan iborat bo'lishi kerak. Masalan: 'Bo'lim boshlig'i'")
        return v.strip()

    @validator("full_name")
    def validate_full_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "To'liq ism kamida 3 belgidan iborat bo'lishi kerak. Masalan: 'Aliyev Valijon'")
        return v.strip()

    @validator("telefon")
    def validate_telefon(cls, v):
        pattern = r"^\+998[0-9]{9}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Telefon raqami +998 bilan boshlanishi va 12 belgidan iborat bo'lishi kerak. Masalan: '+998901234567'")
        return v

    @validator("elektron_pochta")
    def validate_elektron_pochta(cls, v):
        if not v:
            raise ValueError(
                "Elektron pochta bo'sh bo'lmasligi kerak. Masalan: 'example@domain.com'")
        return v


@router.get("/", response_model=list[TarkibiyBolinmaOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TarkibiyBolinma))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni olishda xato: {str(e)}")


@router.post("/for_admin/", response_model=TarkibiyBolinmaOut)
async def create_tarkibiy_bolinma(
    kimligi: str = Form(...),
    full_name: str = Form(...),
    telefon: str = Form(...),
    elektron_pochta: str = Form(...),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = TarkibiyBolinmaCreate(
            kimligi=kimligi,
            full_name=full_name,
            telefon=telefon,
            elektron_pochta=elektron_pochta
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if image:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {image.content_type}. Faqat PNG, JPG, JPEG ruxsat etiladi. Masalan: rasm.jpg"
            )
        filename = f"{uuid4().hex}_{image.filename}"
        file_path = os.path.join(IMAGE_FOLDER, filename)
        try:
            async with aio_open(file_path, "wb") as f:
                await f.write(await image.read())
            image_url = f"/static/images/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Rasmni saqlashda xato: {str(e)}")
    else:
        image_url = "/static/images/default.png"

    new_bolinma = TarkibiyBolinma(
        kimligi=data.kimligi,
        full_name=data.full_name,
        telefon=data.telefon,
        elektron_pochta=data.elektron_pochta,
        image=image_url
    )
    try:
        db.add(new_bolinma)
        await db.commit()
        await db.refresh(new_bolinma)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni saqlashda xato: {str(e)}")
    return new_bolinma


@router.put("/{id}/for_admin/", response_model=TarkibiyBolinmaOut)
async def update_tarkibiy_bolinma(
    id: int,
    kimligi: str = Form(...),
    full_name: str = Form(...),
    telefon: str = Form(...),
    elektron_pochta: str = Form(...),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = TarkibiyBolinmaCreate(
            kimligi=kimligi,
            full_name=full_name,
            telefon=telefon,
            elektron_pochta=elektron_pochta
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = await db.execute(select(TarkibiyBolinma).where(TarkibiyBolinma.id == id))
    bolinma = result.scalar_one_or_none()
    if not bolinma:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    if image:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {image.content_type}. Faqat PNG, JPG, JPEG ruxsat etiladi. Masalan: rasm.jpg"
            )
        old_path = bolinma.image.lstrip("/")
        if os.path.exists(old_path) and "default.png" not in old_path:
            try:
                os.remove(old_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Eski rasmni o'chirishda xato: {str(e)}")

        filename = f"{uuid4().hex}_{image.filename}"
        file_path = os.path.join(IMAGE_FOLDER, filename)
        try:
            async with aio_open(file_path, "wb") as f:
                await f.write(await image.read())
            bolinma.image = f"/static/images/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Rasmni saqlashda xato: {str(e)}")

    bolinma.kimligi = data.kimligi
    bolinma.full_name = data.full_name
    bolinma.telefon = data.telefon
    bolinma.elektron_pochta = data.elektron_pochta

    try:
        await db.commit()
        await db.refresh(bolinma)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni yangilashda xato: {str(e)}")
    return bolinma


@router.delete("/{id}/for_admin/")
async def delete_tarkibiy_bolinma(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(TarkibiyBolinma).where(TarkibiyBolinma.id == id))
    bolinma = result.scalar_one_or_none()
    if not bolinma:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    if bolinma.image and "default.png" not in bolinma.image:
        old_path = bolinma.image.lstrip("/")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Rasmni o'chirishda xato: {str(e)}")

    try:
        await db.delete(bolinma)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
