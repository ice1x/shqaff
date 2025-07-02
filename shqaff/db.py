from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import DATABASE_URL
from .models import Base


engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = scoped_session(sessionmaker(bind=engine))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
