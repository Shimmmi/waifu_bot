from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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

# Обслуживание статических файлов
if Path("webapp").exists():
    app.mount("/webapp", StaticFiles(directory="webapp"), name="webapp")

# Тестовые данные вайфу из базы данных
WAIFU_DATA = {
    "wf_ddd65e42": {
        "id": "wf_ddd65e42",
        "name": "Ava",
        "rarity": "Common",
        "race": "Demon",
        "profession": "Warrior",
        "nationality": "Japanese",
        "level": 1,
        "xp": 158,
        "stats": {
            "power": 13,
            "charm": 6,
            "luck": 7,
            "affection": 8,
            "intellect": 8,
            "speed": 5
        },
        "dynamic": {
            "mood": 78,
            "loyalty": 60,
            "bond": 0,
            "energy": 80,
            "favor": 0
        },
        "tags": ["demon", "warrior"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_cfe1d04d": {
        "id": "wf_cfe1d04d",
        "name": "Amelia",
        "rarity": "Uncommon",
        "race": "Human",
        "profession": "Mage",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 17,
            "charm": 12,
            "luck": 15,
            "affection": 11,
            "intellect": 10,
            "speed": 15
        },
        "dynamic": {
            "mood": 90,
            "loyalty": 64,
            "bond": 0,
            "energy": 84,
            "favor": 0
        },
        "tags": ["human", "mage"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_dcbada59": {
        "id": "wf_dcbada59",
        "name": "Chloe",
        "rarity": "Uncommon",
        "race": "Elf",
        "profession": "Archer",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 20,
            "charm": 15,
            "luck": 10,
            "affection": 13,
            "intellect": 11,
            "speed": 13
        },
        "dynamic": {
            "mood": 72,
            "loyalty": 57,
            "bond": 0,
            "energy": 98,
            "favor": 0
        },
        "tags": ["elf", "archer"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_0a40c958": {
        "id": "wf_0a40c958",
        "name": "Amelia",
        "rarity": "Common",
        "race": "Cyborg",
        "profession": "Engineer",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 9,
            "charm": 9,
            "luck": 6,
            "affection": 7,
            "intellect": 9,
            "speed": 5
        },
        "dynamic": {
            "mood": 92,
            "loyalty": 48,
            "bond": 0,
            "energy": 89,
            "favor": 0
        },
        "tags": ["cyborg", "engineer"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_014a3db7": {
        "id": "wf_014a3db7",
        "name": "Mia",
        "rarity": "Common",
        "race": "Spirit",
        "profession": "Healer",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 5,
            "charm": 9,
            "luck": 10,
            "affection": 8,
            "intellect": 5,
            "speed": 5
        },
        "dynamic": {
            "mood": 81,
            "loyalty": 69,
            "bond": 0,
            "energy": 93,
            "favor": 0
        },
        "tags": ["spirit", "healer"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_d13973bc": {
        "id": "wf_d13973bc",
        "name": "Shreya",
        "rarity": "Common",
        "race": "Demon",
        "profession": "Assassin",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 12,
            "charm": 6,
            "luck": 6,
            "affection": 8,
            "intellect": 7,
            "speed": 9
        },
        "dynamic": {
            "mood": 92,
            "loyalty": 76,
            "bond": 0,
            "energy": 85,
            "favor": 0
        },
        "tags": ["demon", "assassin"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_db6afaaf": {
        "id": "wf_db6afaaf",
        "name": "Chloe",
        "rarity": "Common",
        "race": "Spirit",
        "profession": "Priest",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 6,
            "charm": 6,
            "luck": 6,
            "affection": 6,
            "intellect": 8,
            "speed": 7
        },
        "dynamic": {
            "mood": 76,
            "loyalty": 41,
            "bond": 0,
            "energy": 90,
            "favor": 0
        },
        "tags": ["spirit", "priest"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_23d91003": {
        "id": "wf_23d91003",
        "name": "Olivia",
        "rarity": "Common",
        "race": "Cyborg",
        "profession": "Technician",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 15,
            "charm": 8,
            "luck": 6,
            "affection": 6,
            "intellect": 6,
            "speed": 10
        },
        "dynamic": {
            "mood": 76,
            "loyalty": 64,
            "bond": 0,
            "energy": 89,
            "favor": 0
        },
        "tags": ["cyborg", "technician"],
        "created_at": "2025-01-01T00:00:00"
    },
    "wf_9656bbe0": {
        "id": "wf_9656bbe0",
        "name": "Isabella",
        "rarity": "Common",
        "race": "Fairy",
        "profession": "Enchanter",
        "nationality": "Japanese",
        "level": 1,
        "xp": 0,
        "stats": {
            "power": 12,
            "charm": 7,
            "luck": 9,
            "affection": 8,
            "intellect": 5,
            "speed": 8
        },
        "dynamic": {
            "mood": 96,
            "loyalty": 66,
            "bond": 0,
            "energy": 89,
            "favor": 0
        },
        "tags": ["fairy", "enchanter"],
        "created_at": "2025-01-01T00:00:00"
    }
}

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
    """Получение данных вайфу для WebApp"""
    # Проверяем, есть ли данные для этого ID
    if waifu_id in WAIFU_DATA:
        return WAIFU_DATA[waifu_id]
    
    # Если данных нет, возвращаем тестовую вайфу
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
