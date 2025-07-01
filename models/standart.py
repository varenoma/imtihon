from sqlalchemy import Column, Integer, String, Text
from core.database import Base


class Standart(Base):
    __tablename__ = "standartlar"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    pdf = Column(String)
