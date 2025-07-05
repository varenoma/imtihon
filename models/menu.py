from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    submenus = relationship(
        "SubMenu",
        back_populates="menu",
        cascade="all, delete",
        lazy="selectin"
    )


class SubMenu(Base):
    __tablename__ = "submenus"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    url = Column(String(255), nullable=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    menu = relationship(
        "Menu",
        back_populates="submenus",
        lazy="selectin"
    )
