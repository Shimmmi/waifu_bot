from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any
import os

from bot.db import SessionLocal
from bot.models import Waifu
from bot.services.waifu_generator import calculate_waifu_power

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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/waifu/{waifu_id}")
async def get_waifu_card(waifu_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение данных вайфу для WebApp"""
    try:
        # Получаем вайфу из базы данных
        waifu = db.query(Waifu).filter(Waifu.id == waifu_id).first()
        
        if not waifu:
            raise HTTPException(status_code=404, detail="Вайфу не найдена")
        
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
        
        return waifu_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@app.get("/")
async def read_root():
    """Главная страница WebApp"""
    return FileResponse("webapp/waifu-card.html")

@app.get("/waifu-card/{waifu_id}")
async def waifu_card_page(waifu_id: str):
    """Страница карточки вайфу"""
    return FileResponse("webapp/waifu-card.html")

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "message": "Waifu Bot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
