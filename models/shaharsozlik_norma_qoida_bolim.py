from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class ShaharsozlikNormaQoidaBolim(Base):
    __tablename__ = "shaharsozlik_norma_qoida_bolim"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    tizim = Column(Integer, ForeignKey("tizim.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    tizim_obj = relationship(
        "Tizim",
        back_populates="bolimlar",
        passive_deletes=True
    )

    guruhlar = relationship(
        "Guruh",
        back_populates="bolim_obj",
        cascade="all, delete",
        passive_deletes=True
    )
