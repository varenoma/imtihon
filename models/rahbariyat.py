from sqlalchemy import Column, Integer, String
from core.database import Base


class Rahbariyat(Base):
    __tablename__ = "rahbariyat"

    id = Column(Integer, primary_key=True, index=True)
    positions = Column(String)
    full_name = Column(String)
    qabul_kunlari = Column(String)
    telefon = Column(String)
    elektron_pochta = Column(String)
    mutahassisligi = Column(String)
    rasm = Column(String)
