from pydantic import BaseModel


class TashkilTuzilmaOut(BaseModel):
    id: int
    image: str

    class Config:
        from_attributes = True
