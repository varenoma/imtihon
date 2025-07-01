from sqlalchemy import Column, Integer, String
from core.database import Base


class TmsitiBoglanishMalumoti(Base):
    __tablename__ = "tmsiti_boglanish_malumoti"

    id = Column(Integer, primary_key=True, index=True)
    joylashuv = Column(String)
    manzil = Column(String)
    email = Column(String)
    qoshimcha_email = Column(String)
    tel_raqam = Column(String)
