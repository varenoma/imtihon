import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.tashkiliy_tuzilma import TashkilTuzilma
from schemas.tashkil_tuzilma import TashkilTuzilmaOut
from auth.dependencies import get_current_admin
from aiofiles import open as aio_open
from dotenv import load_dotenv

router = APIRouter(prefix="/tashkil-tuzilma", tags=["Tashkil Tuzilma"])

load_dotenv()

IMAGE_FOLDER = os.getenv("IMAGE_FOLDER")


@router.get("/", response_model=list[TashkilTuzilmaOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TashkilTuzilma))
    return result.scalars().all()


@router.post("/for_admin/", response_model=TashkilTuzilmaOut)
async def create(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    allowed_types = ["image/png", "image/jpeg"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Yaroqsiz fayl turi: {image.content_type}. Faqat PNG, JPG, JPEG ruxsat etiladi"
        )

    filename = f"{uuid4().hex}_{image.filename}"
    path = os.path.join(IMAGE_FOLDER, filename)

    async with aio_open(path, "wb") as f:
        await f.write(await image.read())

    new = TashkilTuzilma(image=f"/static/images/{filename}")
    db.add(new)
    await db.commit()
    await db.refresh(new)
    return new


@router.put("/{id}/for_admin/", response_model=TashkilTuzilmaOut)
async def update(
    id: int,
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(TashkilTuzilma).where(TashkilTuzilma.id == id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, detail="Topilmadi")

    if image:
        allowed_types = ["image/png", "image/jpeg"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Yaroqsiz fayl turi: {image.content_type}. Faqat PNG, JPG, JPEG ruxsat etiladi"
            )

        old_path = row.image.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

        filename = f"{uuid4().hex}_{image.filename}"
        path = os.path.join(IMAGE_FOLDER, filename)
        async with aio_open(path, "wb") as f:
            await f.write(await image.read())
        row.image = f"/static/images/{filename}"

    await db.commit()
    await db.refresh(row)
    return row


@router.delete("/{id}/for_admin/")
async def delete(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(TashkilTuzilma).where(TashkilTuzilma.id == id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, detail="Topilmadi")

    if row.image:
        path = row.image.lstrip("/")
        if os.path.exists(path):
            os.remove(path)

    await db.delete(row)
    await db.commit()
    return {"message": "O'chirildi"}
