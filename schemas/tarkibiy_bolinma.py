from pydantic import BaseModel, EmailStr


class TarkibiyBolinmaOut(BaseModel):
    id: int
    kimligi: str
    full_name: str
    telefon: str
    elektron_pochta: str
    image: str | None

    class Config:
        from_attributes = True
