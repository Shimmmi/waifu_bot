from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import os
import sys
import logging
from pathlib import Path
import hmac
import hashlib
import base64
import json
from urllib.parse import parse_qs, unquote

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

# Import and register skills router
try:
    from bot.api_skills import router as skills_router
    app.include_router(skills_router)
except ImportError:
    logger.warning("Skills API not available - skills_router not imported")

# Функция для получения сессии базы данных
def get_db():
    if SessionLocal is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_telegram_user_id(request: Request) -> Optional[int]:
    """Извлечение user_id из Telegram WebApp initData"""
    try:
        # Получаем initData из заголовка или query параметров
        init_data = request.headers.get("X-Telegram-Init-Data") or request.query_params.get("initData")
        
        if not init_data:
            logger.warning("⚠️ No initData provided")
            return None
        
        # Декодируем initData
        data_str = unquote(init_data)
        parsed_data = parse_qs(data_str)
        
        # Получаем user из parsed_data
        user_str = parsed_data.get('user', [None])[0]
        if not user_str:
            logger.warning("⚠️ No user data in initData")
            return None
        
        # Парсим JSON с данными пользователя
        user_data = json.loads(user_str)
        telegram_user_id = user_data.get('id')
        
        if telegram_user_id:
            logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        return telegram_user_id
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to extract user ID from initData: {e}")
        return None

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
        logger.info(f"   Nationality: {waifu.nationality}")
        
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
            "is_favorite": waifu.is_favorite or False,
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
async def read_root(request: Request):
    """Главная страница WebApp"""
    logger.info(f"🌐 Root WebApp request: {request.url}")
    logger.info(f"📱 User Agent: {request.headers.get('user-agent', 'Unknown')}")
    
    webapp_path = Path(__file__).parent.parent.parent / "webapp" / "index.html"
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
async def get_profile(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение данных профиля пользователя (из Telegram WebApp initData)"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/profile")
        logger.info(f"🌐 Request URL: {request.url}")
        logger.info(f"📱 User Agent: {request.headers.get('user-agent', 'Unknown')}")
        
        if User is None or SessionLocal is None:
            logger.error("❌ Database models not configured")
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if telegram_user_id:
            # Find user by Telegram user ID
            user = db.query(User).filter(User.tg_id == telegram_user_id).first()
            logger.info(f"🔍 Searching for user with tg_id={telegram_user_id}")
        else:
            # Fallback to first user if initData not available (for testing)
            logger.warning("⚠️ No telegram_user_id, using first user as fallback")
            user = db.query(User).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get active waifu
        active_waifu = None
        waifu = db.query(Waifu).filter(
            Waifu.owner_id == user.id,
            Waifu.is_active == True
        ).first()
        
        logger.info(f"🔍 Active waifu query: owner_id={user.id}")
        logger.info(f"   Active waifu found: {waifu.name if waifu else 'None'}")
        
        if waifu:
            power = calculate_waifu_power(waifu.__dict__)
            active_waifu = {
                "id": waifu.id,
                "name": waifu.name,
                "level": waifu.level,
                "power": power,
                "image_url": waifu.image_url,
                "stats": waifu.stats,
                "dynamic": waifu.dynamic,
                "is_active": True
            }
        
        # Get user skill points
        try:
            from bot.models import UserSkills
            user_skills = db.query(UserSkills).filter(UserSkills.user_id == user.id).first()
            skill_points = user_skills.skill_points if user_skills else 0
        except:
            skill_points = 0
        
        profile_data = {
            "username": user.username or "username",
            "user_id": user.tg_id,
            "gold": user.coins,
            "gems": user.gems,
            "tokens": getattr(user, 'tokens', 0),
            "skill_points": skill_points,
            "level": getattr(user, 'account_level', 1),
            "xp": getattr(user, 'global_xp', 0),
            "waifu_sort_preference": getattr(user, 'waifu_sort_preference', 'name'),
            "active_waifu": active_waifu
        }
        
        logger.info(f"✅ Profile data fetched")
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.patch("/api/profile/preferences")
async def update_preferences(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Update user preferences (sort preference, etc.)"""
    try:
        logger.info(f"📡 API REQUEST: PATCH /api/profile/preferences")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Find user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Parse request body
        body = await request.json()
        sort_by = body.get('waifu_sort_preference')
        
        # Validate sort_by value
        valid_sorts = ['name', 'rarity', 'level', 'power', 'race', 'profession', 'nationality']
        if sort_by and sort_by not in valid_sorts:
            raise HTTPException(status_code=400, detail=f"Invalid sort preference: {sort_by}. Valid values: {', '.join(valid_sorts)}")
        
        # Update preference
        user.waifu_sort_preference = sort_by
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Updated sort preference for user {user.id}: {sort_by}")
        
        return {
            "success": True,
            "waifu_sort_preference": user.waifu_sort_preference
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.get("/api/waifus")
async def get_waifus(request: Request, db: Session = Depends(get_db)):
    """Получение списка всех вайфу пользователя"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/waifus")
        
        if User is None or Waifu is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if telegram_user_id:
            # Find user by Telegram user ID
            user = db.query(User).filter(User.tg_id == telegram_user_id).first()
            logger.info(f"🔍 Searching for user with tg_id={telegram_user_id}")
        else:
            # Fallback to first user if initData not available (for testing)
            logger.warning("⚠️ No telegram_user_id, using first user as fallback")
            user = db.query(User).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get all waifus for user
        waifus = db.query(Waifu).filter(Waifu.owner_id == user.id).all()
        
        waifu_list = []
        for waifu in waifus:
            power = calculate_waifu_power(waifu.__dict__)
            waifu_list.append({
                "id": waifu.id,
                "name": waifu.name,
                "level": waifu.level,
                "power": power,
                "rarity": waifu.rarity,
                "race": waifu.race,
                "profession": waifu.profession,
                "nationality": waifu.nationality,
                "image_url": waifu.image_url,
                "stats": waifu.stats,
                "dynamic": waifu.dynamic,
                "is_active": waifu.is_active or False,
                "is_favorite": waifu.is_favorite or False
            })
        
        logger.info(f"✅ Fetched {len(waifu_list)} waifus")
        return waifu_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.post("/api/waifu/{waifu_id}/set-active")
async def set_active_waifu(waifu_id: str, request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Установить вайфу как активную"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/waifu/{waifu_id}/set-active")
        
        if Waifu is None or User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for set-active")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get waifu
        waifu = db.query(Waifu).filter(Waifu.id == waifu_id).first()
        if not waifu:
            raise HTTPException(status_code=404, detail="Вайфу не найдена")
        
        # Check if waifu belongs to user
        if waifu.owner_id != user.id:
            logger.warning(f"⚠️ User {user.id} tried to set waifu {waifu_id} as active, but it belongs to user {waifu.owner_id}")
            raise HTTPException(status_code=403, detail="Эта вайфу вам не принадлежит")
        
        # Set all user's waifus to inactive
        db.query(Waifu).filter(
            Waifu.owner_id == user.id
        ).update({"is_active": False})
        
        # Set this waifu to active
        waifu.is_active = True
        db.commit()
        
        logger.info(f"✅ Waifu {waifu_id} set as active for user {user.id}")
        return {"success": True, "message": "Вайфу установлена как активная"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.post("/api/waifu/{waifu_id}/toggle-favorite")
async def toggle_favorite(waifu_id: str, request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Переключить статус избранного для вайфу"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/waifu/{waifu_id}/toggle-favorite")
        
        if Waifu is None or User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for toggle-favorite")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get waifu
        waifu = db.query(Waifu).filter(Waifu.id == waifu_id).first()
        if not waifu:
            raise HTTPException(status_code=404, detail="Вайфу не найдена")
        
        # Check if waifu belongs to user
        if waifu.owner_id != user.id:
            logger.warning(f"⚠️ User {user.id} tried to toggle favorite for waifu {waifu_id}, but it belongs to user {waifu.owner_id}")
            raise HTTPException(status_code=403, detail="Эта вайфу вам не принадлежит")
        
        # Toggle favorite status
        waifu.is_favorite = not waifu.is_favorite
        db.commit()
        
        status = "добавлена в избранное" if waifu.is_favorite else "удалена из избранного"
        logger.info(f"✅ Waifu {waifu_id} {status} for user {user.id}")
        return {"success": True, "message": f"Вайфу {status}", "is_favorite": waifu.is_favorite}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.post("/api/summon")
async def summon_waifus(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Призыв вайфу (1 или 10)"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/summon")
        
        if Waifu is None or User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for summon")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get request body
        body = await request.json()
        count = body.get("count", 1)
        
        if count not in [1, 10]:
            raise HTTPException(status_code=400, detail="Можно призвать только 1 или 10 вайфу")
        
        cost = 100 if count == 1 else 1000
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Check if user has enough coins
        if user.coins < cost:
            raise HTTPException(status_code=400, detail=f"Недостаточно монет! Нужно {cost} монет.")
        
        # Import waifu generator
        from bot.services.waifu_generator import generate_waifu, calculate_waifu_power
        from sqlalchemy import func
        
        # Get max card number
        max_card = db.query(func.max(Waifu.card_number)).scalar() or 0
        
        # Generate waifus
        summoned_waifus = []
        for i in range(count):
            waifu_data = generate_waifu(max_card + 1 + i, user.id)
            waifu = Waifu(**waifu_data)
            db.add(waifu)
            
            # Calculate power for response
            power = calculate_waifu_power(waifu_data)
            
            summoned_waifus.append({
                "id": waifu.id,
                "card_number": waifu.card_number,
                "name": waifu.name,
                "rarity": waifu.rarity,
                "race": waifu.race,
                "profession": waifu.profession,
                "nationality": waifu.nationality,
                "power": power,
                "level": waifu.level,
                "image_url": waifu.image_url
            })
        
        # Deduct coins
        user.coins -= cost
        
        # Commit transaction
        db.commit()
        
        logger.info(f"✅ Summoned {count} waifu(s) for user {user.id}, cost: {cost} coins")
        return {
            "success": True,
            "summoned": summoned_waifus,
            "remaining_coins": user.coins
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.get("/api/shop")
async def get_shop_items(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение списка товаров магазина"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/shop")
        
        # Define shop items (in future, these can be stored in database)
        shop_items = [
            {
                "id": "wbox_1",
                "name": "📦 Обычная коробка вайфу",
                "description": "Случайная вайфу обычной редкости",
                "price": 100,
                "currency": "gold",
                "category": "lootbox",
                "emoji": "📦"
            },
            {
                "id": "wbox_10",
                "name": "📦 Комбо-набор (10 шт)",
                "description": "10 коробок вайфу со скидкой!",
                "price": 900,
                "currency": "gold",
                "category": "lootbox",
                "emoji": "📦"
            },
            {
                "id": "gem_100",
                "name": "💎 100 Гемов",
                "description": "Пополнение счета гемами",
                "price": 500,
                "currency": "gold",
                "category": "currency",
                "emoji": "💎"
            },
            {
                "id": "energy_restore",
                "name": "⚡ Полное восстановление энергии",
                "description": "Все вайфу восстанавливают энергию на 100%",
                "price": 50,
                "currency": "gems",
                "category": "utility",
                "emoji": "⚡"
            }
        ]
        
        logger.info(f"✅ Returning {len(shop_items)} shop items")
        return {"items": shop_items}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.post("/api/shop/purchase")
async def purchase_item(request: Request, item_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Покупка товара в магазине"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/shop/purchase (item_id: {item_id})")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Define shop items with purchase logic
        shop_items = {
            "wbox_1": {
                "name": "📦 Обычная коробка вайфу",
                "price": 100,
                "currency": "gold",
                "action": "waifu_box_single"
            },
            "wbox_10": {
                "name": "📦 Комбо-набор (10 шт)",
                "price": 900,
                "currency": "gold",
                "action": "waifu_box_multi"
            },
            "gem_100": {
                "name": "💎 100 Гемов",
                "price": 500,
                "currency": "gold",
                "action": "add_gems"
            },
            "energy_restore": {
                "name": "⚡ Полное восстановление энергии",
                "price": 50,
                "currency": "gems",
                "action": "restore_energy"
            }
        }
        
        if item_id not in shop_items:
            raise HTTPException(status_code=404, detail="Товар не найден")
        
        item = shop_items[item_id]
        
        # Check user has enough currency
        user_currency = getattr(user, item["currency"], 0)
        if user_currency < item["price"]:
            raise HTTPException(status_code=400, detail=f"Недостаточно {item['currency']}")
        
        # Deduct currency
        setattr(user, item["currency"], user_currency - item["price"])
        
        # Execute action
        if item["action"] == "add_gems":
            user.gems += 100
            result_message = "✅ Получено 100 гемов!"
        elif item["action"] == "restore_energy":
            # Restore energy for all waifus
            from bot.services.waifu_generator import Waifu
            waifus = db.query(Waifu).filter(Waifu.owner_id == user.id).all()
            for waifu in waifus:
                if waifu.dynamic:
                    waifu.dynamic["energy"] = 100
            result_message = "✅ Энергия всех вайфу восстановлена!"
        else:
            # For waifu boxes, just return success - actual waifu generation happens elsewhere
            result_message = "✅ Покупка успешна! Призовите вайфу через меню"
        
        db.commit()
        
        logger.info(f"✅ Purchase successful: {item_id} by user {user.id}")
        return {
            "success": True,
            "message": result_message,
            "new_balance": {
                "gold": user.coins,
                "gems": user.gems
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.get("/api/skills")
async def get_skills_tree(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение дерева навыков и текущего прогресса пользователя"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/skills")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Define skill tree structure
        skills_tree = {
            "combat": [
                {
                    "id": "attack_boost",
                    "name": "Усиление атаки",
                    "description": "Увеличивает урон на 5% за уровень",
                    "max_level": 10,
                    "icon": "⚔️"
                },
                {
                    "id": "defense_boost",
                    "name": "Усиление защиты",
                    "description": "Увеличивает защиту на 5% за уровень",
                    "max_level": 10,
                    "icon": "🛡️"
                }
            ],
            "economy": [
                {
                    "id": "gold_bonus",
                    "name": "Золотой бонус",
                    "description": "Получайте на 10% больше золота",
                    "max_level": 5,
                    "icon": "💰"
                },
                {
                    "id": "xp_bonus",
                    "name": "Бонус опыта",
                    "description": "Получайте на 10% больше опыта",
                    "max_level": 5,
                    "icon": "⭐"
                }
            ],
            "waifu": [
                {
                    "id": "waifu_power",
                    "name": "Мощь вайфу",
                    "description": "Увеличивает мощность вайфу на 5%",
                    "max_level": 10,
                    "icon": "💪"
                },
                {
                    "id": "waifu_energy",
                    "name": "Энергия вайфу",
                    "description": "Увеличивает максимальную энергию на 10",
                    "max_level": 5,
                    "icon": "⚡"
                }
            ]
        }
        
        # Get user's current skills
        user_skills = getattr(user, 'user_skills', {}) or {}
        skill_points = getattr(user, 'skill_points', 0)
        
        logger.info(f"✅ Returning skills tree for user {user.id}")
        return {
            "skill_points": skill_points,
            "skills": skills_tree,
            "user_skills": user_skills
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.post("/api/skills/upgrade")
async def upgrade_skill(request: Request, skill_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Улучшение навыка"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/skills/upgrade (skill_id: {skill_id})")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Check skill points
        skill_points = getattr(user, 'skill_points', 0)
        if skill_points < 1:
            raise HTTPException(status_code=400, detail="Недостаточно очков навыков")
        
        # Get current skills
        user_skills = getattr(user, 'user_skills', {}) or {}
        
        # Define max levels
        max_levels = {
            "attack_boost": 10, "defense_boost": 10,
            "gold_bonus": 5, "xp_bonus": 5,
            "waifu_power": 10, "waifu_energy": 5
        }
        
        current_level = user_skills.get(skill_id, 0)
        max_level = max_levels.get(skill_id, 10)
        
        if current_level >= max_level:
            raise HTTPException(status_code=400, detail="Навык уже максимального уровня")
        
        # Upgrade skill
        user_skills[skill_id] = current_level + 1
        user.user_skills = user_skills
        user.skill_points = skill_points - 1
        
        db.commit()
        
        logger.info(f"✅ Skill {skill_id} upgraded to level {user_skills[skill_id]}")
        return {
            "success": True,
            "message": f"Навык улучшен до уровня {user_skills[skill_id]}",
            "skill_points": user.skill_points,
            "user_skills": user_skills
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.get("/api/quests")
async def get_quests(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение списка ежедневных заданий"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/quests")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Define quests (in future, these can be stored in database)
        quests = [
            {
                "id": "daily_message",
                "name": "Отправить 10 сообщений",
                "description": "Напишите 10 сообщений в группе",
                "icon": "💬",
                "reward_gold": 50,
                "reward_xp": 10,
                "progress": 0,
                "target": 10,
                "completed": False
            },
            {
                "id": "daily_waifu",
                "name": "Призвать вайфу",
                "description": "Призовите хотя бы одну вайфу",
                "icon": "🎴",
                "reward_gold": 100,
                "reward_xp": 20,
                "progress": 0,
                "target": 1,
                "completed": False
            },
            {
                "id": "daily_active",
                "name": "Быть активным",
                "description": "Получите 100 опыта за день",
                "icon": "⭐",
                "reward_gold": 150,
                "reward_xp": 30,
                "progress": getattr(user, 'daily_xp', 0),
                "target": 100,
                "completed": getattr(user, 'daily_xp', 0) >= 100
            }
        ]
        
        logger.info(f"✅ Returning {len(quests)} quests")
        return {"quests": quests}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.get("/api/daily-bonus-status")
async def get_daily_bonus_status(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Проверка доступности ежедневного бонуса"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/daily-bonus-status")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for daily bonus status")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Check daily bonus availability
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        last_daily = user.last_daily.replace(tzinfo=None) if user.last_daily else datetime(1970, 1, 1)
        
        can_claim = now - last_daily >= timedelta(hours=24)
        
        if can_claim:
            time_remaining = 0
        else:
            time_remaining = int((timedelta(hours=24) - (now - last_daily)).total_seconds())
        
        logger.info(f"✅ Daily bonus status: can_claim={can_claim}, time_remaining={time_remaining}")
        
        return {
            "can_claim": can_claim,
            "time_remaining": time_remaining,
            "streak": user.daily_streak
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@app.post("/api/daily-bonus")
async def claim_daily_bonus(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение ежедневного бонуса"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/daily-bonus")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for daily bonus")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Check daily bonus availability
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        last_daily = user.last_daily.replace(tzinfo=None) if user.last_daily else datetime(1970, 1, 1)
        
        if now - last_daily < timedelta(hours=24):
            time_left = timedelta(hours=24) - (now - last_daily)
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            raise HTTPException(status_code=400, detail=f"Бонус недоступен. Осталось: {hours}ч {minutes}м")
        
        # Give bonus
        user.coins += 100
        user.daily_streak += 1
        user.last_daily = now
        db.commit()
        
        logger.info(f"✅ Daily bonus claimed for user {user.id}, new balance: {user.coins}")
        
        return {
            "success": True,
            "coins_added": 100,
            "new_balance": user.coins,
            "streak": user.daily_streak
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@app.get("/api/upgrade/waifus")
async def get_upgrade_waifus(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение списка вайфу для прокачки (исключая максимального уровня)"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/upgrade/waifus")
        
        if Waifu is None or User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for upgrade waifus")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get waifus that can be upgraded (not at max level)
        # Max levels: Common=30, Uncommon=35, Rare=40, Epic=45, Legendary=50
        max_levels = {
            'Common': 30,
            'Uncommon': 35,
            'Rare': 40,
            'Epic': 45,
            'Legendary': 50
        }
        
        waifus = db.query(Waifu).filter(Waifu.owner_id == user.id).all()
        
        upgradeable_waifus = []
        for waifu in waifus:
            max_level = max_levels.get(waifu.rarity, 30)
            if waifu.level < max_level:
                # Calculate power for display
                from bot.services.waifu_generator import calculate_waifu_power
                power = calculate_waifu_power({
                    'stats': waifu.stats or {},
                    'dynamic': waifu.dynamic or {},
                    'level': waifu.level
                })
                
                upgradeable_waifus.append({
                    "id": waifu.id,
                    "card_number": waifu.card_number,
                    "name": waifu.name,
                    "rarity": waifu.rarity,
                    "race": waifu.race,
                    "profession": waifu.profession,
                    "nationality": waifu.nationality,
                    "level": waifu.level,
                    "max_level": max_level,
                    "power": power,
                    "image_url": waifu.image_url,
                    "xp": waifu.xp or 0
                })
        
        logger.info(f"✅ Found {len(upgradeable_waifus)} upgradeable waifus")
        
        return {
            "waifus": upgradeable_waifus
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@app.get("/api/upgrade/sacrifice-candidates")
async def get_sacrifice_candidates(request: Request, target_waifu_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение списка вайфу для жертвования (исключая целевую вайфу)"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/upgrade/sacrifice-candidates?target_waifu_id={target_waifu_id}")
        
        if Waifu is None or User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for sacrifice candidates")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get all waifus except the target one (ID is string in database)
        waifus = db.query(Waifu).filter(
            Waifu.owner_id == user.id,
            Waifu.id != target_waifu_id
        ).all()
        
        candidates = []
        for waifu in waifus:
            # Calculate XP value (based on level and rarity)
            xp_value = calculate_sacrifice_xp(waifu)
            
            # Calculate power for display
            from bot.services.waifu_generator import calculate_waifu_power
            power = calculate_waifu_power({
                'stats': waifu.stats or {},
                'dynamic': waifu.dynamic or {},
                'level': waifu.level
            })
            
            candidates.append({
                "id": waifu.id,
                "card_number": waifu.card_number,
                "name": waifu.name,
                "rarity": waifu.rarity,
                "race": waifu.race,
                "profession": waifu.profession,
                "nationality": waifu.nationality,
                "level": waifu.level,
                "power": power,
                "xp_value": xp_value,
                "image_url": waifu.image_url
            })
        
        logger.info(f"✅ Found {len(candidates)} sacrifice candidates")
        
        return {
            "candidates": candidates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@app.post("/api/upgrade/perform")
async def perform_upgrade(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Выполнение улучшения вайфу"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/upgrade/perform")
        
        if Waifu is None or User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")
        
        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)
        
        if not telegram_user_id:
            logger.warning("⚠️ No initData provided for upgrade")
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        logger.info(f"✅ Extracted Telegram user ID: {telegram_user_id}")
        
        # Get request body
        body = await request.json()
        target_waifu_id = body.get("target_waifu_id")
        sacrifice_waifu_ids = body.get("sacrifice_waifu_ids", [])
        
        if not target_waifu_id or not sacrifice_waifu_ids:
            raise HTTPException(status_code=400, detail="Не указана целевая вайфу или вайфу для жертвования")
        
        # Get user
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Get target waifu
        target_waifu = db.query(Waifu).filter(
            Waifu.id == target_waifu_id,
            Waifu.owner_id == user.id
        ).first()
        
        if not target_waifu:
            raise HTTPException(status_code=404, detail="Целевая вайфу не найдена")
        
        # Get sacrifice waifus
        sacrifice_waifus = db.query(Waifu).filter(
            Waifu.id.in_(sacrifice_waifu_ids),
            Waifu.owner_id == user.id
        ).all()
        
        if len(sacrifice_waifus) != len(sacrifice_waifu_ids):
            raise HTTPException(status_code=400, detail="Некоторые вайфу для жертвования не найдены")
        
        # Calculate total XP to add
        total_xp = sum(calculate_sacrifice_xp(waifu) for waifu in sacrifice_waifus)
        
        # Add XP to target waifu
        old_level = target_waifu.level
        old_xp = target_waifu.xp or 0
        target_waifu.xp = old_xp + total_xp
        
        # Check for level up
        new_level = calculate_level_from_xp(target_waifu.xp)
        level_gained = new_level - old_level
        target_waifu.level = new_level
        
        # Delete sacrifice waifus
        for waifu in sacrifice_waifus:
            db.delete(waifu)
        
        db.commit()
        
        logger.info(f"✅ Upgrade completed: +{total_xp} XP, level {old_level} → {new_level}")
        
        return {
            "success": True,
            "target_waifu_id": target_waifu_id,
            "xp_added": total_xp,
            "old_level": old_level,
            "new_level": new_level,
            "level_gained": level_gained,
            "sacrificed_count": len(sacrifice_waifus)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


def calculate_sacrifice_xp(waifu) -> int:
    """Calculate XP value when sacrificing a waifu"""
    # Base XP from level
    base_xp = waifu.level * 50
    
    # Rarity multiplier
    rarity_multipliers = {
        'Common': 1.0,
        'Uncommon': 1.2,
        'Rare': 1.5,
        'Epic': 2.0,
        'Legendary': 3.0
    }
    
    multiplier = rarity_multipliers.get(waifu.rarity, 1.0)
    return int(base_xp * multiplier)


def calculate_level_from_xp(xp: int) -> int:
    """Calculate level from total XP"""
    level = 1
    total_xp_needed = 0
    
    while True:
        xp_for_next = int(100 * (level ** 1.1))
        if total_xp_needed + xp_for_next > xp:
            break
        total_xp_needed += xp_for_next
        level += 1
        
        # Safety check to prevent infinite loop
        if level > 100:
            break
    
    return level


@app.get("/api/avatars")
async def get_avatars(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получение списка доступных аватаров"""
    try:
        logger.info(f"📡 API REQUEST: GET /api/avatars")
        
        # List of available avatars from GitHub
        avatars = [
            {"id": "avatar1", "name": "Аватар 1", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar1.jpg"},
            {"id": "avatar2", "name": "Аватар 2", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar2.jpg"},
            {"id": "avatar3", "name": "Аватар 3", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar3.jpg"},
            {"id": "avatar4", "name": "Аватар 4", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar4.jpg"},
            {"id": "avatar5", "name": "Аватар 5", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar5.jpg"},
            {"id": "avatar6", "name": "Аватар 6", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar6.jpg"},
            {"id": "avatar7", "name": "Аватар 7", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar7.jpg"},
            {"id": "avatar8", "name": "Аватар 8", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar8.jpg"},
            {"id": "avatar9", "name": "Аватар 9", "url": "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/avatars/avatar9.jpg"}
        ]
        
        logger.info(f"✅ Returning {len(avatars)} avatars")
        return {"avatars": avatars}
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

@app.post("/api/avatar/select")
async def select_avatar(request: Request, avatar_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Выбор аватара пользователя"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/avatar/select (avatar_id: {avatar_id})")
        
        if User is None:
            raise HTTPException(status_code=500, detail="Database models not configured")

        # Extract Telegram user ID from initData
        telegram_user_id = get_telegram_user_id(request)

        if not telegram_user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Update user's avatar (we'll add avatar field to User model later)
        # For now, just return success
        db.commit()

        logger.info(f"✅ Avatar {avatar_id} selected for user {user.id}")
        return {
            "success": True,
            "message": f"✅ Аватар выбран!",
            "avatar_id": avatar_id
        }

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
