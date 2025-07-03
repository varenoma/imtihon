from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Tizim(Base):
    __tablename__ = "tizim"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # bog‘langan bolimlar
    bolimlar = relationship(
        "ShaharsozlikNormaQoidaBolim",
        back_populates="tizim_obj",
        cascade="all, delete",
        passive_deletes=True
    )
