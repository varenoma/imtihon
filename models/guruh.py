from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Guruh(Base):
    __tablename__ = "guruhlar"

    id = Column(Integer, primary_key=True, index=True)
    shifr = Column(String)
    hujjat_nomi = Column(String)
    link = Column(String)
    pdf = Column(String)
    bolim = Column(Integer, ForeignKey(
        "shaharsozlik_norma_qoida_bolim.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    bolim_obj = relationship(
        "ShaharsozlikNormaQoidaBolim",
        back_populates="guruhlar",
        passive_deletes=True
    )
