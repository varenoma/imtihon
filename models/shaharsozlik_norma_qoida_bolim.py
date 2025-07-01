from sqlalchemy import Column, Integer, String
from core.database import Base


class ShaharsozlikNormaQoidaBolim(Base):
    __tablename__ = "shaharsozlik_norma_qoida_bolim"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
