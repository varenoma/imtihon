from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

from models.tizim import Tizim
from models.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolim

router = APIRouter(prefix="/full_tizim", tags=['Full Tizim'])


@router.get("/")
async def get_full_tizim(session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(Tizim).options(
            selectinload(Tizim.bolimlar).selectinload(
                ShaharsozlikNormaQoidaBolim.guruhlar)
        )
    )
    tizimlar = result.scalars().unique().all()
    return tizimlar
