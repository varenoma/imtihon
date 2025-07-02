from pydantic import BaseModel, Field


class ShaharsozlikNormaQoidaBolimOut(BaseModel):
    id: int = Field(..., description="Bo'limning noyob identifikatori")
    name: str = Field(..., description="Bo'lim nomi. Masalan: 'Norma bo'limi'")

    class Config:
        from_attributes = True
