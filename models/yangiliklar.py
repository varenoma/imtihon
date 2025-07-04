from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from core.database import Base


class Yangilik(Base):
    __tablename__ = "yangiliklar"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    text = Column(Text)
    rasm = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
