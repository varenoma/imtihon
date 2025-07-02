from pydantic import BaseModel, Field
from schemas.shaharsozlik_norma_qoida_bolim import ShaharsozlikNormaQoidaBolimOut


class GuruhOut(BaseModel):
    id: int = Field(..., description="Guruhning noyob identifikatori")
    shifr: str = Field(..., description="Shifr. Masalan: 'ABC-123'")
    hujjat_nomi: str = Field(...,
                             description="Hujjat nomi. Masalan: 'Shaharsozlik qoidasi'")
    link: str | None = Field(
        None, description="Hujjat linki. Masalan: 'https://example.com'")
    pdf: str | None = Field(
        None, description="PDF fayl yo'li. Masalan: '/static/pdfs/document.pdf'")
    bolim: int = Field(..., description="Bo'lim ID'si. Masalan: 1")
    bolim_obj: ShaharsozlikNormaQoidaBolimOut = Field(
        ..., description="Bog'langan bo'lim ma'lumotlari")

    class Config:
        from_attributes = True
