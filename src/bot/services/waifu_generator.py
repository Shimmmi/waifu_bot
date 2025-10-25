import uuid
import random
import datetime
import logging
from typing import Dict, List, Optional
from ..data_tables import (
    RACES, PROFESSIONS, NATIONALITIES, RARITIES, STATS_DISTRIBUTION, 
    NAMES_BY_NATIONALITY, TAGS,
    WAIFU_IMAGES_BY_RACE, WAIFU_IMAGES_BY_PROFESSION, WAIFU_IMAGES_BY_NATIONALITY
)

logger = logging.getLogger(__name__)

# Curated list of anime waifu images (safe for work)
# Using placeholder service that generates consistent anime-style avatars
# Format: https://api.dicebear.com/7.x/[style]/svg?seed=[unique_seed]
WAIFU_IMAGES = [
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Bella",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Sophie",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Luna",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Mia",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Zoe",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Lily",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Chloe",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Emma",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Ava",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Aria",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Nora",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Ruby",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Jade",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Rose",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Iris",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Maya",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Nova",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Star",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Sky",
    "https://api.dicebear.com/7.x/adventurer/svg?seed=Dawn",
]


def get_waifu_image(race: str = None, profession: str = None, nationality: str = None) -> str:
    """
    Get a waifu image based on race, profession, or nationality
    Priority: race > profession > nationality > fallback
    Returns image URL
    """
    # Try to get image by race first (most distinctive)
    if race and race in WAIFU_IMAGES_BY_RACE:
        images = WAIFU_IMAGES_BY_RACE[race]
        if images:
            image_url = random.choice(images)
            logger.info(f"🎨 Selected {race} waifu image: {image_url}")
            return image_url
    
    # Try profession if race doesn't have images
    if profession and profession in WAIFU_IMAGES_BY_PROFESSION:
        images = WAIFU_IMAGES_BY_PROFESSION[profession]
        if images:
            image_url = random.choice(images)
            logger.info(f"🎨 Selected {profession} waifu image: {image_url}")
            return image_url
    
    # Try nationality as last resort
    if nationality and nationality in WAIFU_IMAGES_BY_NATIONALITY:
        images = WAIFU_IMAGES_BY_NATIONALITY[nationality]
        if images:
            image_url = random.choice(images)
            logger.info(f"🎨 Selected {nationality} waifu image: {image_url}")
            return image_url
    
    # Fallback to generic images
    image_url = random.choice(WAIFU_IMAGES)
    logger.info(f"🎨 Selected fallback waifu image: {image_url}")
    return image_url


def generate_waifu(card_number: int, owner_id: int = None) -> Dict:
    """Генерирует новую вайфу с случайными характеристиками"""
    
    # Выбираем редкость (веса: 60%, 25%, 10%, 4%, 1%)
    rarity = random.choices(
        list(RARITIES.keys()), 
        weights=[60, 25, 10, 4, 1]
    )[0]
    
    # Выбираем расу, профессию и национальность
    race = random.choice(RACES)
    profession = random.choice(PROFESSIONS)
    nationality = random.choice(NATIONALITIES)
    
    # Генерируем характеристики на основе редкости
    base_stats = STATS_DISTRIBUTION[rarity]
    stats = {}
    for stat_name, (min_val, max_val) in base_stats.items():
        stats[stat_name] = random.randint(min_val, max_val)
    
    # Генерируем динамические характеристики
    dynamic = {
        "mood": random.randint(70, 100),
        "loyalty": random.randint(40, 80),
        "bond": 0,
        "energy": random.randint(80, 100),
        "favor": 0
    }
    
    # Выбираем имя на основе национальности
    name = random.choice(NAMES_BY_NATIONALITY[nationality])
    
    # Генерируем теги (2-4 случайных тега)
    num_tags = random.randint(2, 4)
    tags = random.sample(TAGS, num_tags)
    
    # Создаем уникальный ID
    waifu_id = f"wf_{uuid.uuid4().hex[:8]}"
    
    # Get anime image based on waifu characteristics
    image_url = get_waifu_image(race=race, profession=profession, nationality=nationality)
    
    return {
        "id": waifu_id,
        "card_number": card_number,
        "name": name,
        "rarity": rarity,
        "race": race,
        "profession": profession,
        "nationality": nationality,
        "image_url": image_url,  # Now fetches real anime images!
        "owner_id": owner_id,
        "level": 1,
        "xp": 0,
        "stats": stats,
        "dynamic": dynamic,
        "tags": tags,
        "created_at": datetime.datetime.utcnow()
    }


def generate_waifu_name(nationality: str = None) -> str:
    """Генерирует имя для вайфу"""
    if nationality and nationality in NAMES_BY_NATIONALITY:
        return random.choice(NAMES_BY_NATIONALITY[nationality])
    else:
        # Случайная национальность
        nat = random.choice(list(NAMES_BY_NATIONALITY.keys()))
        return random.choice(NAMES_BY_NATIONALITY[nat])


def calculate_waifu_power(waifu: Dict) -> int:
    """Вычисляет общую силу вайфу"""
    stats = waifu.get("stats", {})
    dynamic = waifu.get("dynamic", {})
    
    # Базовая сила из характеристик
    base_power = sum(stats.values())
    
    # Бонусы от динамических характеристик
    mood_bonus = dynamic.get("mood", 50) * 0.1
    loyalty_bonus = dynamic.get("loyalty", 50) * 0.05
    
    # Бонус за уровень
    level = waifu.get("level", 1)
    level_bonus = level * 2
    
    total_power = base_power + mood_bonus + loyalty_bonus + level_bonus
    return int(total_power)


def get_rarity_color(rarity: str) -> str:
    """Возвращает цвет для редкости"""
    colors = {
        "Common": "⚪",
        "Uncommon": "🟢", 
        "Rare": "🔵",
        "Epic": "🟣",
        "Legendary": "🟡"
    }
    return colors.get(rarity, "⚪")


def format_waifu_card(waifu: Dict) -> str:
    """Форматирует карточку вайфу для отображения"""
    from bot.services.level_up import level_up_service
    
    rarity_icon = get_rarity_color(waifu["rarity"])
    power = calculate_waifu_power(waifu)
    
    # Get XP progress info
    current_xp = waifu.get('xp', 0)
    current_level = waifu.get('level', 1)
    xp_info = level_up_service.get_xp_progress_info(current_xp, current_level)
    
    # Format XP progress bar
    xp_in_level = xp_info['xp_in_current_level']
    xp_needed = xp_info['xp_needed_in_level']
    progress = xp_info['progress_percentage']
    
    card = f"""
{rarity_icon} <b>{waifu['name']}</b> [{waifu['rarity']}]
🏷️ {waifu['race']} • {waifu['profession']} • {waifu['nationality']}
⚡ Уровень: {waifu['level']} | 💪 Сила: {power}

✨ <b>Опыт:</b> {xp_in_level}/{xp_needed} ({progress}%)

📊 <b>Характеристики:</b>
💪 Сила: {waifu['stats'].get('power', 0)}
💖 Очарование: {waifu['stats'].get('charm', 0)}
🍀 Удача: {waifu['stats'].get('luck', 0)}
❤️ Привязанность: {waifu['stats'].get('affection', 0)}
🧠 Интеллект: {waifu['stats'].get('intellect', 0)}
⚡ Скорость: {waifu['stats'].get('speed', 0)}

💭 <b>Состояние:</b>
😊 Настроение: {waifu['dynamic'].get('mood', 0)}%
💝 Лояльность: {waifu['dynamic'].get('loyalty', 0)}%
⚡ Энергия: {waifu['dynamic'].get('energy', 0)}%

🏷️ <i>{', '.join(waifu['tags'])}</i>
"""
    return card.strip()
