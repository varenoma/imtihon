import re
from fastapi import APIRouter, Form, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from models.qonun_qaror_farmon import QonunQarorFarmon
from schemas.qonun_qaror_farmon import QonunQarorFarmonOut
from auth.dependencies import get_current_admin
from datetime import date
from dotenv import load_dotenv
from pydantic import BaseModel, validator

router = APIRouter(prefix="/qonun-qaror-farmonlar",
                   tags=["Qonun, Qaror, Farmonlar"])

load_dotenv()


class QonunQarorFarmonCreate(BaseModel):
    title: str
    type: str
    content: str
    number: str
    date: date
    source: str

    @validator("title")
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError(
                "Nomi kamida 5 belgidan iborat bo'lishi kerak. Masalan: 'Mehnat to'g'risida qonun'")
        return v.strip()

    @validator("type")
    def validate_type(cls, v):
        allowed_types = ["Qonun", "Qaror", "Farmon"]
        if v not in allowed_types:
            raise ValueError(
                f"Tur faqat {', '.join(allowed_types)} bo'lishi mumkin. Masalan: 'Qonun'")
        return v

    @validator("content")
    def validate_content(cls, v):
        if len(v.strip()) < 10:
            raise ValueError(
                "Matn kamida 10 belgidan iborat bo'lishi kerak. Masalan: 'Ushbu hujjatda...'")
        return v.strip()

    @validator("number")
    def validate_number(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "Raqam kamida 3 belgidan iborat bo'lishi kerak. Masalan: '123- removes sensitive information'")
        return v.strip()

    @validator("source")
    def validate_source(cls, v):
        if len(v.strip()) < 3:
            raise ValueError(
                "Manba kamida 3 belgidan iborat bo'lishi kerak. Masalan: 'Xalq so'zi'")
        return v.strip()


@router.get(
    "/",
    response_model=list[QonunQarorFarmonOut],
    summary="Barcha qonun, qaror va farmonlarni olish",
    description="Barcha qonun, qaror va farmonlarni sahifalarga bo'lib olish. Limit (bir sahifadagi yozuvlar soni) va offset (qaysi yozuvdan boshlash) parametrlari yordamida so'rovni boshqarish mumkin. Ma'lumotlar sana bo'yicha kamayish tartibida qaytariladi.",
    response_description="Qonun, qaror va farmonlar ro'yxati, har birida id, nomi, turi, matni, raqami, sanasi va manbasi."
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Bir sahifadagi yozuvlar soni (1-100). Masalan: 10"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Qaysi yozuvdan boshlash (0 yoki undan katta). Masalan: 0"
    )
):
    try:
        result = await db.execute(
            select(QonunQarorFarmon).offset(offset).limit(
                limit).order_by(QonunQarorFarmon.date.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni olishda xato: {str(e)}")


@router.post(
    "/for_admin/",
    response_model=QonunQarorFarmonOut,
    summary="Yangi qonun, qaror yoki farmon yaratish",
    description="Faqat adminlar uchun: Yangi qonun, qaror yoki farmon yaratish. Barcha maydonlar majburiy: title (kamida 5 belgi), type ('Qonun', 'Qaror', 'Farmon'), content (kamida 10 belgi), number (kamida 3 belgi), date (YYYY-MM-DD formatida), source (kamida 3 belgi).",
    response_description="Yaratilgan qonun, qaror yoki farmon ma'lumotlari."
)
async def create_qonun_qaror_farmon(
    title: str = Form(...,
                      description="Nomi, kamida 5 belgi. Masalan: 'Mehnat to'g'risida qonun'"),
    type: str = Form(..., description="Tur, faqat 'Qonun', 'Qaror' yoki 'Farmon'. Masalan: 'Qonun'"),
    content: str = Form(...,
                        description="Matn, kamida 10 belgi. Masalan: 'Ushbu hujjatda...'"),
    number: str = Form(...,
                       description="Raqam, kamida 3 belgi. Masalan: '123-AB'"),
    date: date = Form(...,
                      description="Sana, YYYY-MM-DD formatida. Masalan: '2025-07-02'"),
    source: str = Form(...,
                       description="Manba, kamida 3 belgi. Masalan: 'Xalq so'zi'"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = QonunQarorFarmonCreate(
            title=title,
            type=type,
            content=content,
            number=number,
            date=date,
            source=source
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    new_qonun = QonunQarorFarmon(
        title=data.title,
        type=data.type,
        content=data.content,
        number=data.number,
        date=data.date,
        source=data.source
    )
    try:
        db.add(new_qonun)
        await db.commit()
        await db.refresh(new_qonun)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni saqlashda xato: {str(e)}")
    return new_qonun


@router.put(
    "/{id}/for_admin/",
    response_model=QonunQarorFarmonOut,
    summary="Qonun, qaror yoki farmonni yangilash",
    description="Faqat adminlar uchun: Mavjud qonun, qaror yoki farmonni yangilash. ID orqali hujjat topiladi va yangi ma'lumotlar (title, type, content, number, date, source) bilan yangilanadi.",
    response_description="Yangilangan qonun, qaror yoki farmon ma'lumotlari."
)
async def update_qonun_qaror_farmon(
    id: int,
    title: str = Form(...,
                      description="Nomi, kamida 5 belgi. Masalan: 'Mehnat to'g'risida qonun'"),
    type: str = Form(..., description="Tur, faqat 'Qonun', 'Qaror' yoki 'Farmon'. Masalan: 'Qonun'"),
    content: str = Form(...,
                        description="Matn, kamida 10 belgi. Masalan: 'Ushbu hujjatda...'"),
    number: str = Form(...,
                       description="Raqam, kamida 3 belgi. Masalan: '123-AB'"),
    date: date = Form(...,
                      description="Sana, YYYY-MM-DD formatida. Masalan: '2025-07-02'"),
    source: str = Form(...,
                       description="Manba, kamida 3 belgi. Masalan: 'Xalq so'zi'"),
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    try:
        data = QonunQarorFarmonCreate(
            title=title,
            type=type,
            content=content,
            number=number,
            date=date,
            source=source
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    result = await db.execute(select(QonunQarorFarmon).where(QonunQarorFarmon.id == id))
    qonun = result.scalar_one_or_none()
    if not qonun:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    qonun.title = data.title
    qonun.type = data.type
    qonun.content = data.content
    qonun.number = data.number
    qonun.date = data.date
    qonun.source = data.source

    try:
        await db.commit()
        await db.refresh(qonun)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni yangilashda xato: {str(e)}")
    return qonun


@router.delete(
    "/{id}/for_admin/",
    summary="Qonun, qaror yoki farmonni o'chirish",
    description="Faqat adminlar uchun: ID orqali qonun, qaror yoki farmonni o'chirish.",
    response_description="O'chirish muvaffaqiyatli amalga oshirildi."
)
async def delete_qonun_qaror_farmon(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    result = await db.execute(select(QonunQarorFarmon).where(QonunQarorFarmon.id == id))
    qonun = result.scalar_one_or_none()
    if not qonun:
        raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

    try:
        await db.delete(qonun)
        await db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ma'lumotlarni o'chirishda xato: {str(e)}")
    return {"message": "Muvaffaqiyatli o'chirildi"}
