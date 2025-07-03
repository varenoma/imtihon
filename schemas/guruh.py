import re
from pydantic import BaseModel, Field, validator, HttpUrl
from datetime import datetime
from schemas.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolimOut


class GuruhCreate(BaseModel):
    shifr: str = Field(..., min_length=3,
                       description="Shifr, kamida 3 belgi. Masalan: 'ABC-123'")
    hujjat_nomi: str = Field(..., min_length=5,
                             description="Hujjat nomi, kamida 5 belgi. Masalan: 'Shaharsozlik qoidasi'")
    link: str | None = Field(
        None, description="Hujjat linki, to'g'ri URL formati. Masalan: 'https://example.com'")
    pdf: str | None = Field(
        None, description="PDF fayl yo'li. Masalan: '/static/pdfs/document.pdf'")
    bolim: int = Field(...,
                       description="Shaharsozlik norma qoida bo'limi ID'si. Masalan: 1")

    @validator("shifr")
    def validate_shifr(cls, v):
        return v.strip()

    @validator("hujjat_nomi")
    def validate_hujjat_nomi(cls, v):
        return v.strip()

    @validator("link")
    def validate_link(cls, v):
        if v and not re.match(r"^https?://", v):
            raise ValueError(
                "Link to'g'ri URL bo'lishi kerak. Masalan: 'https://example.com'")
        return v


class GuruhOut(BaseModel):
    id: int
    shifr: str
    hujjat_nomi: str
    link: str | None
    pdf: str | None
    bolim: int
    created_at: datetime
    bolim_obj: ShaharsozlikNormaQoidaBolimOut

    class Config:
        from_attributes = True
