from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./db/tmsiti.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session_Local = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


def get_db():
    db = Session_Local()
    try:
        yield db
    finally:
        db.close()
