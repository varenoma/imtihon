from sqlalchemy import Column, Integer, String
from core.database import Base


class TarkibiyBolinma(Base):
    __tablename__ = "tarkibiy_bolinmalar"

    id = Column(Integer, primary_key=True, index=True)
    kimligi = Column(String)
    full_name = Column(String)
    telefon = Column(String)
    elektron_pochta = Column(String)
    image = Column(String)
