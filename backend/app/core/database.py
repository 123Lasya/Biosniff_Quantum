import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session, DeclarativeBase
from app.core.config import settings

# Engine configuration supporting MySQL (production) and SQLite (testing)
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///./"):
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_filename = db_url.replace("sqlite:///./", "")
    db_path = os.path.join(backend_dir, db_filename).replace("\\", "/")
    db_url = f"sqlite:///{db_path}"

connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.x models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Ensures session cleanup on completion or exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
