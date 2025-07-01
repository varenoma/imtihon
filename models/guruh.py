from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base


class Guruh(Base):
    __tablename__ = "guruhlar"

    id = Column(Integer, primary_key=True, index=True)
    shifr = Column(String)
    hujjat_nomi = Column(String)
    link = Column(String)
    pdf = Column(String)
    bolim = Column(Integer, ForeignKey("shaharsozlik_norma_qoida_bolim.id"))

    bolim_obj = relationship("ShaharsozlikNormaQoidaBolim", backref="guruhlar")
