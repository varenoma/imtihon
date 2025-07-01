from sqlalchemy import Column, Integer, String
from core.database import Base


class TashkilTuzilma(Base):
    __tablename__ = "tashkil_tuzilma"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)
