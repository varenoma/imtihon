from pydantic import BaseModel


class RahbariyatBase(BaseModel):
    positions: str
    full_name: str
    qabul_kunlari: str
    telefon: str
    elektron_pochta: str
    mutahassisligi: str
    rasm: str

    class Config:
        from_attributes = True


class RahbariyatCreate(BaseModel):
    positions: str
    full_name: str
    qabul_kunlari: str
    telefon: str
    elektron_pochta: str
    mutahassisligi: str


class RahbariyatOut(RahbariyatBase):
    id: int
