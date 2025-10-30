from typing import AsyncIterator
import logging
import sys

from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.orm import sessionmaker, Session

from bot.config import get_settings

# Import all models to ensure they are registered with SQLAlchemy
try:
    from bot.models import Base, User, WaifuInstance, WaifuTemplate
    from bot.models.skills import UserSkills, Skill, UserSkillLevel, SkillPointEarning
    logger = logging.getLogger(__name__)
    logger.info("✅ Skills models imported successfully")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Error importing skills models: {e}")
    # If skills models are not available yet, don't fail
    pass

try:
    settings = get_settings()
    logger.info(f"📊 Configuring database connection...")
    
    # Check if DATABASE_URL is set
    if not settings.database_url:
        logger.error("❌ DATABASE_URL environment variable is not set!")
        raise ValueError("DATABASE_URL must be set in environment variables")
    
    logger.info(f"✅ DATABASE_URL found (length: {len(settings.database_url)} chars)")
    logger.info(f"   Database type: {settings.database_url.split(':')[0]}")
    
except Exception as e:
    logger.error(f"❌ Failed to load settings: {e}")
    raise


def create_engine():
    try:
        # Заменяем asyncpg на psycopg2
        database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        logger.info(f"🔗 Creating database engine...")
        logger.info(f"   URL scheme: {database_url.split(':')[0]}")
        
        engine = create_sync_engine(
            database_url,
            echo=(settings.env == "development"),
            pool_pre_ping=True,
        )
        
        logger.info(f"✅ Database engine created successfully")
        return engine
        
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        logger.error(f"   DATABASE_URL starts with: {settings.database_url[:20]}...")
        raise


engine = create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()



