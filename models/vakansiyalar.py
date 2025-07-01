from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from core.database import Base


class Vakansiya(Base):
    __tablename__ = "vakansiyalar"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    bolim = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
