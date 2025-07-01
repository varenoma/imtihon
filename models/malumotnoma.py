from sqlalchemy import Column, Integer, String
from core.database import Base


class Malumotnoma(Base):
    __tablename__ = "malumotnoma"

    id = Column(Integer, primary_key=True, index=True)
    nomi = Column(String)
    hujjat = Column(String)
