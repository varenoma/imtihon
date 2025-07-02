from pydantic import BaseModel


class TmsitiHaqidaOut(BaseModel):
    id: int
    text: str
    pdf: str

    class Config:
        from_attributes = True
