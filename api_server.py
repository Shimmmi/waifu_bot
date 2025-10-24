from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

app = FastAPI(title="Waifu Bot API", version="1.0.0")

# CORS настройки для Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web.telegram.org", "https://telegram.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Главная страница WebApp"""
    webapp_path = Path("webapp/waifu-card.html")
    if webapp_path.exists():
        return FileResponse(str(webapp_path))
    else:
        return {"message": "Waifu Bot WebApp", "status": "running"}

@app.get("/waifu-card/{waifu_id}")
async def waifu_card_page(waifu_id: str):
    """Страница карточки вайфу"""
    webapp_path = Path("webapp/waifu-card.html")
    if webapp_path.exists():
        return FileResponse(str(webapp_path))
    else:
        return {"message": f"Waifu card page for ID: {waifu_id}", "status": "running"}

@app.get("/api/waifu/{waifu_id}")
async def get_waifu_card(waifu_id: str):
    """Получение данных вайфу для WebApp (заглушка)"""
    # Возвращаем тестовые данные
    return {
        "id": waifu_id,
        "name": "Тестовая вайфу",
        "rarity": "Rare",
        "race": "Human",
        "profession": "Mage",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 50,
            "charm": 60,
            "luck": 40,
            "affection": 30,
            "intellect": 70,
            "speed": 45
        },
        "dynamic": {
            "mood": 80,
            "loyalty": 60,
            "energy": 90
        },
        "tags": ["cute", "magical"],
        "created_at": "2025-01-01T00:00:00"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "message": "Waifu Bot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
