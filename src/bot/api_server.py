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

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))
logger.info("🌐 Starting Waifu Bot API Server...")

try:
    from db import SessionLocal
    from models import Waifu
    from services.waifu_generator import calculate_waifu_power
except ImportError:
    # Если не можем импортировать, создаем заглушки
    SessionLocal = None
    Waifu = None
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
    import logging
    logger = logging.getLogger(__name__)
    
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
        logger.info(f"   Dynamic: {waifu.dynamic}")
        
        # Формируем ответ
        waifu_data = {
            "id": waifu.id,
            "name": waifu.name,
            "rarity": waifu.rarity,
            "race": waifu.race,
            "profession": waifu.profession,
            "nationality": waifu.nationality,
            "level": waifu.level,
            "xp": waifu.xp,
            "stats": waifu.stats,
            "dynamic": waifu.dynamic,
            "tags": waifu.tags,
            "created_at": waifu.created_at.isoformat()
        }
        
        logger.info(f"📤 SENDING TO CLIENT:")
        logger.info(f"   XP: {waifu_data['xp']}")
        logger.info(f"   Dynamic: {waifu_data['dynamic']}")
        
        return waifu_data
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

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

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "message": "Waifu Bot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
