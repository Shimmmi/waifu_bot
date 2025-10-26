from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Добавляем путь к проекту для правильного импорта модулей
current_dir = Path(__file__).parent  # src/bot/
src_dir = current_dir.parent  # src/
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

logger.info("🌐 Starting Waifu Bot API Server...")
logger.info(f"   Current directory: {current_dir}")
logger.info(f"   Python path: {sys.path[:3]}")

try:
    # Import using bot.module_name since src/ is in path
    from bot.db import SessionLocal
    from bot.models import Waifu, User
    from bot.services.waifu_generator import calculate_waifu_power
    logger.info("✅ Database modules imported successfully")
    logger.info(f"   SessionLocal: {SessionLocal}")
    logger.info(f"   Waifu model: {Waifu}")
    logger.info(f"   User model: {User}")
except ImportError as e:
    logger.error(f"❌ Failed to import database modules: {e}", exc_info=True)
    # Если не можем импортировать, создаем заглушки
    SessionLocal = None
    Waifu = None
    User = None
    calculate_waifu_power = lambda x: 0

app = FastAPI(title="Waifu Bot API", version="1.0.0")

# CORS настройки для Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web.telegram.org", "https://telegram.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Функция для получения сессии базы данных
def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/waifu/{waifu_id}")
async def get_waifu_card(waifu_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение данных вайфу для WebApp"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/waifu/{waifu_id}")
        
        if Waifu is None:
            logger.error("❌ Database models not configured")
            raise HTTPException(status_code=500, detail="Database models not configured")
            
        # Получаем вайфу из базы данных
        logger.info(f"🔍 Querying database for waifu_id: {waifu_id}")
        waifu = db.query(Waifu).filter(Waifu.id == waifu_id).first()
        
        if not waifu:
            logger.warning(f"⚠️ Waifu not found: {waifu_id}")
            raise HTTPException(status_code=404, detail="Вайфу не найдена")
        
        logger.info(f"✅ FETCHED FROM DB: Waifu {waifu.id} ({waifu.name})")
        logger.info(f"   XP: {waifu.xp}")
        logger.info(f"   Image URL: {waifu.image_url}")
        logger.info(f"   Dynamic: {waifu.dynamic}")
        
        # Формируем ответ
        waifu_data = {
            "id": waifu.id,
            "name": waifu.name,
            "rarity": waifu.rarity,
            "race": waifu.race,
            "profession": waifu.profession,
            "nationality": waifu.nationality,
            "image_url": waifu.image_url,  # Include image URL
            "level": waifu.level,
            "xp": waifu.xp,
            "stats": waifu.stats,
            "dynamic": waifu.dynamic,
            "tags": waifu.tags,
            "created_at": waifu.created_at.isoformat() if waifu.created_at else None
        }
        
        logger.info(f"📤 SENDING TO CLIENT:")
        logger.info(f"   XP: {waifu_data['xp']}")
        logger.info(f"   Image URL: {waifu_data['image_url']}")
        logger.info(f"   Dynamic: {waifu_data['dynamic']}")
        
        return waifu_data
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

# Статическая раздача файлов из webapp директории
webapp_dir = Path(__file__).parent.parent.parent / "webapp"
if webapp_dir.exists():
    app.mount("/webapp", StaticFiles(directory=str(webapp_dir)), name="webapp")
    logger.info(f"✅ Static files mounted from: {webapp_dir}")

@app.get("/")
async def read_root():
    """Главная страница WebApp"""
    webapp_path = Path(__file__).parent.parent.parent / "webapp" / "waifu-card.html"
    if webapp_path.exists():
        return FileResponse(str(webapp_path))
    else:
        return {"message": "Waifu Bot WebApp", "status": "running"}

@app.get("/waifu-card/{waifu_id}")
async def waifu_card_page(waifu_id: str):
    """Страница карточки вайфу"""
    webapp_path = Path(__file__).parent.parent.parent / "webapp" / "waifu-card.html"
    if webapp_path.exists():
        return FileResponse(str(webapp_path))
    else:
        return {"message": f"Waifu card page for ID: {waifu_id}", "status": "running"}

@app.get("/api/profile")
async def get_profile(user_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение данных профиля пользователя"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/profile?user_id={user_id}")
        
        if User is None or SessionLocal is None:
            logger.error("❌ Database models not configured")
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Get user
        user = db.query(User).filter(User.tg_id == user_id).first()
        if not user:
            logger.warning(f"⚠️ User not found: {user_id}")
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get active waifu
        active_waifu = None
        waifu = db.query(Waifu).filter(
            Waifu.owner_id == user_id,
            Waifu.is_active == True
        ).first()
        
        if waifu:
            power = calculate_waifu_power(waifu.__dict__)
            active_waifu = {
                "name": waifu.name,
                "level": waifu.level,
                "power": power,
                "image_url": waifu.image_url
            }
        
        profile_data = {
            "display_name": user.display_name or "Пользователь",
            "username": user.username or "username",
            "coins": user.coins,
            "gems": user.gems,
            "account_level": 1,  # Placeholder for future system
            "active_waifu": active_waifu
        }
        
        logger.info(f"✅ Profile data fetched for user {user_id}")
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "message": "Waifu Bot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
