from sqlalchemy import Column, Integer, Text
from core.database import Base


class ManagementSystem(Base):
    __tablename__ = "management_system"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
