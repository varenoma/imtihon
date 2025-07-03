from sqlalchemy import Column, Text, Integer

from core.database import Base


class ManagementSystemPage(Base):
    __tablename__ = "management_system_page"

    id = Column(Integer, primary_key=True)
    page = Column(Text)
