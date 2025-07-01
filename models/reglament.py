from sqlalchemy import Column, Integer, String
from core.database import Base


class Reglament(Base):
    __tablename__ = "reglamentlar"

    id = Column(Integer, primary_key=True, index=True)
    shifri = Column(String)
    nomi = Column(String)
    link = Column(String)
    pdf = Column(String)
