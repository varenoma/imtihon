from pydantic import BaseModel, Field, validator
from datetime import datetime


class TizimCreate(BaseModel):
    name: str = Field(..., min_length=1,
                      description="Tizim nomi. Masalan: 'Tizim 1'")

    @validator("name")
    def validate_name(cls, v):
        return v.strip()


class TizimOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
