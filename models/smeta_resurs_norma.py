from sqlalchemy import Column, Integer, String
from core.database import Base


class SmetaResursNorma(Base):
    __tablename__ = "smeta_resurs_normalari"

    id = Column(Integer, primary_key=True, index=True)
    yangi_ShNQ_raqami = Column(String)
    yangilangan_ShNQ_nomi = Column(String)
    ShNQ_raqami = Column(String)
    ShNQ_nomi = Column(String)
    pdf = Column(String)
