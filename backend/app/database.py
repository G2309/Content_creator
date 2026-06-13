"""Configuración de SQLAlchemy y sesiones."""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,    # detecta conexiones muertas (importante en Railway)
    pool_recycle=300,      # recicla cada 5 min
    echo=settings.is_development,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI: entrega una sesión y la cierra al terminar el request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
