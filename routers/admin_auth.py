from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.database import get_db
from models.admin import Admin
from models.blacklisted_token import BlacklistedToken
from auth.token import create_access_token
from auth.utils import verify_password
from auth.dependencies import get_current_admin
from schemas.admin import AdminOut

router = APIRouter(prefix="/admin-auth", tags=["Admin Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


class AdminCreate(BaseModel):
    username: str = Field(
        ...,
        description="Foydalanuvchi nomi. 3-50 belgi oralig'ida bo'lishi kerak.",
        min_length=3,
        max_length=50
    )
    password: str = Field(
        ...,
        description="Parol. Kamida 8 belgi bo'lishi kerak.",
        min_length=8
    )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Admin).where(Admin.username == form_data.username))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=400, detail="Noto'g'ri foydalanuvchi nomi yoki parol")

    token = create_access_token({"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=AdminOut)
async def get_me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


@router.post("/register", response_model=AdminOut)
async def register(
    admin_data: AdminCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    try:
        # Username noyobligini tekshirish
        result = await db.execute(select(Admin).where(Admin.username == admin_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail="Bu foydalanuvchi nomi allaqachon mavjud")

        # Parolni hash qilish
        hashed_password = pwd_context.hash(admin_data.password)

        # Yangi admin yaratish
        new_admin = Admin(
            username=admin_data.username,
            hashed_password=hashed_password
        )
        db.add(new_admin)
        await db.commit()
        await db.refresh(new_admin)
        return new_admin
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yangi admin yaratishda xato yuz berdi: {str(e)}"
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    try:
        token = credentials.credentials
        # Tokenni qora ro'yxatga qo'shish
        blacklisted_token = BlacklistedToken(token=token)
        db.add(blacklisted_token)
        await db.commit()
        return {"message": "Muvaffaqiyatli tizimdan chiqildi"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tizimdan chiqishda xato yuz berdi: {str(e)}"
        )
