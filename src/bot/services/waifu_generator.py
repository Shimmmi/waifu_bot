import uuid
import random
import datetime
from typing import Dict, List
from ..data_tables import (
    RACES, PROFESSIONS, NATIONALITIES, RARITIES, STATS_DISTRIBUTION, 
    NAMES_BY_NATIONALITY, TAGS
)


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
    
    return {
        "id": waifu_id,
        "card_number": card_number,
        "name": name,
        "rarity": rarity,
        "race": race,
        "profession": profession,
        "nationality": nationality,
        "image_url": None,  # Можно добавить генерацию изображений
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
    rarity_icon = get_rarity_color(waifu["rarity"])
    power = calculate_waifu_power(waifu)
    
    card = f"""
{rarity_icon} <b>{waifu['name']}</b> [{waifu['rarity']}]
🏷️ {waifu['race']} • {waifu['profession']} • {waifu['nationality']}
⚡ Уровень: {waifu['level']} | 💪 Сила: {power}

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
