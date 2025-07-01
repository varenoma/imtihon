from sqlalchemy import Column, String, Integer, Text

from core.database import Base


class TmsitiHaqida(Base):
    __tablename__ = "tmsiti_haqida"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    pdf = Column(String)
