from sqlalchemy import Column, Integer, String, Text, Date
from core.database import Base


class QonunQarorFarmon(Base):
    __tablename__ = "qonun_qaror_farmonlar"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)
    content = Column(Text)
    number = Column(String)
    date = Column(Date)
    source = Column(String)
