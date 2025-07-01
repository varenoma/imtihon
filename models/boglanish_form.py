from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from core.database import Base


class BoglanishForm(Base):
    __tablename__ = "boglanish_form"

    id = Column(Integer, primary_key=True, index=True)
    FIO = Column(String)
    email = Column(String)
    tel_raqam = Column(String)
    type = Column(String)
    murojat_matni = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    fayl = Column(String)
