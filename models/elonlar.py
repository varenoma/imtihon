from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from core.database import Base


class Elon(Base):
    __tablename__ = "elonlar"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
