from pydantic import BaseModel, Field, validator
from datetime import datetime
from schemas.tizim import TizimOut


class ShaharsozlikNormaQoidaBolimCreate(BaseModel):
    name: str = Field(..., min_length=1,
                      description="Bo'lim nomi. Masalan: 'Norma bo'limi'")
    tizim: int = Field(..., description="Tizim ID'si. Masalan: 1")

    @validator("name")
    def validate_name(cls, v):
        return v.strip()


class ShaharsozlikNormaQoidaBolimOut(BaseModel):
    id: int
    name: str
    tizim: int
    created_at: datetime
    tizim_obj: TizimOut

    class Config:
        from_attributes = True
