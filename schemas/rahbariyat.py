from pydantic import BaseModel, EmailStr


class RahbariyatOut(BaseModel):
    id: int
    positions: str
    full_name: str
    qabul_kunlari: str
    telefon: str
    elektron_pochta: str
    mutahassisligi: str
    rasm: str

    class Config:
        from_attributes = True
