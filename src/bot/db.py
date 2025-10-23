from typing import AsyncIterator

from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.orm import sessionmaker, Session

from bot.config import get_settings


settings = get_settings()


def create_engine():
    # Заменяем asyncpg на psycopg2
    database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    return create_sync_engine(
        database_url,
        echo=(settings.env == "development"),
        pool_pre_ping=True,
    )


engine = create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()



