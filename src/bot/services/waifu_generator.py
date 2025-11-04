import uuid
import random
import datetime
import logging
import requests
from typing import Dict, List, Optional
from ..data_tables import (
    RACES, PROFESSIONS, NATIONALITIES, RARITIES, STATS_DISTRIBUTION, 
    NAMES_BY_NATIONALITY, TAGS,
    WAIFU_IMAGES_BY_RACE, WAIFU_IMAGES_BY_PROFESSION, WAIFU_IMAGES_BY_NATIONALITY
)

logger = logging.getLogger(__name__)

# Configurable: Maximum number of image variants per profession
# Set this to match the highest variant number you have (e.g., if you have _1 through _10, set this to 10)
MAX_IMAGE_VARIANTS = 10


def check_image_exists(url: str, timeout: int = 2) -> bool:
    """
    Check if an image URL exists by making a HEAD request
    Returns True if image exists (200 or 301/302 redirect), False otherwise
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        # Accept 200 (OK) and 301/302 (redirects)
        return response.status_code in [200, 301, 302]
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False

# Fallback images (should rarely be used since all races have images)
# Using GitHub-hosted images from Human race as fallback
WAIFU_IMAGES = [
    "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_1.jpeg",
    "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_2.jpeg",
    "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_3.jpeg",
    "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_4.jpeg",
    "https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/races/human/Human_5.jpeg",
]


def get_waifu_image(race: str = None, profession: str = None, nationality: str = None) -> str:
    """
    Get a waifu image based on race, profession, and nationality
    Uses new hierarchical structure: race/nationality/profession.jpeg
    Intelligently tries available variants before falling back
    Returns image URL
    """
    logger.debug(f"🎨 Getting image for: race={race}, profession={profession}, nationality={nationality}")
    
    # Map nationality codes to full names
    nationality_map = {
        "JP": "Japanese",
        "CN": "Chinese",
        "KR": "Korean",
        "US": "American",
        "GB": "British",
        "FR": "French",
        "DE": "German",
        "IT": "Italian",
        "RU": "Russian",
        "BR": "Brazilian",
        "IN": "Indian",
        "CA": "Canadian"
    }
    
    # Convert nationality code to full name
    nationality_full = nationality_map.get(nationality, nationality)
    
    # Build hierarchical image URL with smart variant detection
    if race and profession and nationality_full:
        # Smart variant selection: try variants 1-10 in random order
        # This ensures we pick an available variant if it exists
        variants_to_try = list(range(1, MAX_IMAGE_VARIANTS + 1))
        random.shuffle(variants_to_try)
        
        for variant_number in variants_to_try:
            image_url = f"https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/{race}/{nationality_full}/{profession}_{variant_number}.jpeg"
            logger.debug(f"🔍 Checking variant {variant_number}: {profession}_{variant_number}.jpeg")
            
            # Check if this variant actually exists
            if check_image_exists(image_url):
                logger.info(f"✅ Selected image: {race}/{nationality_full}/{profession}_{variant_number}.jpeg (exists)")
                return image_url
            else:
                logger.debug(f"❌ Variant {variant_number} does not exist, trying next...")
        
        # If we tried all variants, default to variant 1 (should always exist)
        image_url = f"https://raw.githubusercontent.com/Shimmmi/waifu_bot/main/waifu-images/{race}/{nationality_full}/{profession}_1.jpeg"
        logger.info(f"✅ Selected default image: {race}/{nationality_full}/{profession}_1.jpeg")
        return image_url
    
    # Fallback if missing any parameter
    logger.warning(f"⚠️  Missing parameters for image selection: race={race}, profession={profession}, nationality={nationality}")
    
    # Try old race-based images as fallback
    if race and race in WAIFU_IMAGES_BY_RACE:
        images = WAIFU_IMAGES_BY_RACE[race]
        if images:
            image_url = random.choice(images)
            logger.info(f"✅ Using fallback race image: {image_url[:60]}...")
            return image_url
    
    # Ultimate fallback to generic images
    image_url = random.choice(WAIFU_IMAGES)
    logger.warning(f"⚠️  Using ultimate fallback image: {image_url[:60]}...")
    return image_url


def generate_waifu(card_number: int, owner_id: int = None, skill_effects: Dict = None) -> Dict:
    """Генерирует новую вайфу с случайными характеристиками
    
    Args:
        card_number: Unique card number
        owner_id: User ID who owns this waifu
        skill_effects: Dictionary of skill effects to apply (for rarity bonuses)
    """
    if skill_effects is None:
        skill_effects = {}
    
    # Base rarity weights: Common 60%, Uncommon 25%, Rare 10%, Epic 4%, Legendary 1%
    weights = [60, 25, 10, 4, 1]
    
    # Apply rarity bonuses from skills
    rare_chance = skill_effects.get('rare_chance', 0.0)
    epic_chance = skill_effects.get('epic_chance', 0.0)
    legendary_chance = skill_effects.get('legendary_chance', 0.0)
    
    # Increase weights for rare rarities, decrease common proportionally
    if rare_chance > 0 or epic_chance > 0 or legendary_chance > 0:
        total_bonus = rare_chance + epic_chance + legendary_chance
        # Redistribute weights: increase rare/epic/legendary, decrease common
        weights[0] = max(1, int(weights[0] * (1 - total_bonus * 0.5)))  # Common
        weights[2] = min(25, int(weights[2] * (1 + rare_chance * 10)))  # Rare
        weights[3] = min(15, int(weights[3] * (1 + epic_chance * 20)))  # Epic
        weights[4] = min(10, int(weights[4] * (1 + legendary_chance * 30)))  # Legendary
        logger.debug(f"🎲 Adjusted rarity weights: {weights} (rare: +{rare_chance*100:.0f}%, epic: +{epic_chance*100:.0f}%, legend: +{legendary_chance*100:.0f}%)")
    
    # Выбираем редкость с модифицированными весами
    rarity = random.choices(
        list(RARITIES.keys()), 
        weights=weights
    )[0]
    
    # Выбираем расу, профессию и национальность
    race = random.choice(list(RACES.keys()))
    profession = random.choice(list(PROFESSIONS.keys()))
    nationality = random.choice(list(NATIONALITIES.keys()))
    
    # Генерируем характеристики на основе редкости
    base_stats = STATS_DISTRIBUTION[rarity]
    stats = {}
    for stat_name, (min_val, max_val) in base_stats.items():
        stats[stat_name] = random.randint(min_val, max_val)
    
    # Calculate base max energy
    base_max_energy = 100
    
    # Apply battery skill bonus for max energy
    if 'max_energy' in skill_effects:
        base_max_energy += int(skill_effects['max_energy'])
    
    # Генерируем динамические характеристики
    dynamic = {
        "mood": random.randint(70, 100),
        "loyalty": 0,  # Лояльность должна быть 0 у новых вайфу
        "bond": 0,  # Будет установлена на основе редкости
        "energy": random.randint(80, base_max_energy),
        "favor": 0
    }
    
    # Устанавливаем ловкость (bond) на основе редкости
    dexterity_ranges = {
        'Common': (5, 10),
        'Uncommon': (10, 15),
        'Rare': (15, 20),
        'Epic': (20, 25),
        'Legendary': (25, 30)
    }
    min_dex, max_dex = dexterity_ranges.get(rarity, (5, 10))
    dynamic["bond"] = random.randint(min_dex, max_dex)
    
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


def generate_premium_waifu(card_number: int, owner_id: int = None, skill_effects: Dict = None) -> Dict:
    """Генерирует премиум вайфу с гарантированной редкостью Rare, Epic или Legendary
    
    Args:
        card_number: Unique card number
        owner_id: User ID who owns this waifu
        skill_effects: Dictionary of skill effects to apply (for stat bonuses)
    """
    if skill_effects is None:
        skill_effects = {}
    
    # Premium rarity weights: Rare 50%, Epic 35%, Legendary 15%
    # Only Rare, Epic, Legendary (no Common/Uncommon)
    premium_rarities = ['Rare', 'Epic', 'Legendary']
    premium_weights = [50, 35, 15]
    
    # Apply rarity bonuses from skills (but keep premium rarities)
    rare_chance = skill_effects.get('rare_chance', 0.0)
    epic_chance = skill_effects.get('epic_chance', 0.0)
    legendary_chance = skill_effects.get('legendary_chance', 0.0)
    
    # Adjust weights if skills are present
    if rare_chance > 0 or epic_chance > 0 or legendary_chance > 0:
        # Increase weights for Epic and Legendary based on skill bonuses
        premium_weights[1] = min(50, int(premium_weights[1] * (1 + epic_chance * 10)))  # Epic
        premium_weights[2] = min(30, int(premium_weights[2] * (1 + legendary_chance * 20)))  # Legendary
        # Decrease Rare proportionally
        premium_weights[0] = 100 - premium_weights[1] - premium_weights[2]
        logger.debug(f"💎 Premium rarity weights adjusted: {premium_weights} (rare: {premium_weights[0]}%, epic: {premium_weights[1]}%, legend: {premium_weights[2]}%)")
    
    # Выбираем редкость из премиум пула
    rarity = random.choices(premium_rarities, weights=premium_weights)[0]
    
    # Выбираем расу, профессию и национальность
    race = random.choice(list(RACES.keys()))
    profession = random.choice(list(PROFESSIONS.keys()))
    nationality = random.choice(list(NATIONALITIES.keys()))
    
    # Генерируем характеристики на основе редкости
    base_stats = STATS_DISTRIBUTION[rarity]
    stats = {}
    for stat_name, (min_val, max_val) in base_stats.items():
        stats[stat_name] = random.randint(min_val, max_val)
    
    # Calculate base max energy
    base_max_energy = 100
    
    # Apply battery skill bonus for max energy
    if 'max_energy' in skill_effects:
        base_max_energy += int(skill_effects['max_energy'])
    
    # Генерируем динамические характеристики
    dynamic = {
        "mood": random.randint(70, 100),
        "loyalty": 0,  # Лояльность должна быть 0 у новых вайфу
        "bond": 0,  # Будет установлена на основе редкости
        "energy": random.randint(80, base_max_energy),
        "favor": 0
    }
    
    # Устанавливаем ловкость (bond) на основе редкости
    dexterity_ranges = {
        'Rare': (15, 20),
        'Epic': (20, 25),
        'Legendary': (25, 30)
    }
    min_dex, max_dex = dexterity_ranges.get(rarity, (15, 20))
    dynamic["bond"] = random.randint(min_dex, max_dex)
    
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
        "image_url": image_url,
        "owner_id": owner_id,
        "level": 1,
        "xp": 0,
        "stats": stats,
        "dynamic": dynamic,
        "tags": tags,
        "created_at": datetime.datetime.utcnow(),
        "is_active": False,
        "is_favorite": False
    }


def generate_waifu_name(nationality: str = None) -> str:
    """Генерирует имя для вайфу"""
    if nationality and nationality in NAMES_BY_NATIONALITY:
        return random.choice(NAMES_BY_NATIONALITY[nationality])
    else:
        # Случайная национальность
        nat = random.choice(list(NAMES_BY_NATIONALITY.keys()))
        return random.choice(NAMES_BY_NATIONALITY[nat])


def calculate_waifu_power(waifu: Dict, skill_effects: Dict = None) -> int:
    """Вычисляет общую силу вайфу с учетом навыков
    
    Args:
        waifu: Dictionary with waifu data (stats, dynamic, level, rarity)
        skill_effects: Dictionary of skill effects to apply
    """
    if skill_effects is None:
        skill_effects = {}
    
    stats = waifu.get("stats", {})
    dynamic = waifu.get("dynamic", {})
    rarity = waifu.get("rarity", "Common")
    
    # Вычисляем базовую силу из характеристик с применением бонусов к каждой
    stat_bonuses = {
        'power': 1.0,
        'intellect': 1.0,
        'charm': 1.0,
        'speed': 1.0,
        'luck': 1.0,
        'affection': 1.0  # affection is a stat too
    }
    
    # Применяем бонусы к характеристикам от тренировок
    if 'power_bonus' in skill_effects:
        stat_bonuses['power'] += skill_effects['power_bonus']
    if 'intellect_bonus' in skill_effects:
        stat_bonuses['intellect'] += skill_effects['intellect_bonus']
    if 'charm_bonus' in skill_effects:
        stat_bonuses['charm'] += skill_effects['charm_bonus']
    if 'speed_bonus' in skill_effects:
        stat_bonuses['speed'] += skill_effects['speed_bonus']
    if 'luck_bonus' in skill_effects:
        stat_bonuses['luck'] += skill_effects['luck_bonus']
    
    # Применяем бонусы к редкости
    rarity_bonus = 1.0
    if rarity in ['Rare', 'Epic', 'Legendary']:
        rare_power_bonus = skill_effects.get('rare_power_bonus', 0.0)
        epic_power_bonus = skill_effects.get('epic_power_bonus', 0.0)
        if rarity == 'Rare':
            rarity_bonus += rare_power_bonus
        elif rarity in ['Epic', 'Legendary']:
            rarity_bonus += epic_power_bonus
    
    # Суммируем характеристики с бонусами
    base_power = 0
    for stat_name, stat_value in stats.items():
        bonus = stat_bonuses.get(stat_name, 1.0)
        base_power += int(stat_value * bonus)
    
    # Применяем глобальный бонус к редкости
    base_power = int(base_power * rarity_bonus)
    
    # Бонусы от динамических характеристик с модификаторами навыков
    mood_bonus_multiplier = 1.0 + skill_effects.get('mood_power_bonus', 0.0)
    loyalty_bonus_multiplier = 1.0 + skill_effects.get('loyalty_power_bonus', 0.0)
    
    mood_bonus = dynamic.get("mood", 50) * 0.1 * mood_bonus_multiplier
    loyalty_bonus = dynamic.get("loyalty", 50) * 0.05 * loyalty_bonus_multiplier
    
    # Бонус за уровень
    level = waifu.get("level", 1)
    level_bonus = level * 2
    
    total_power = base_power + mood_bonus + loyalty_bonus + level_bonus
    
    # Применяем бонусы от коллекции (synergy, harmony)
    # Эти бонусы рассчитываются на уровне API и добавляются в skill_effects
    collection_bonus = skill_effects.get('collection_power_bonus', 0.0)
    if collection_bonus > 0:
        total_power = int(total_power * (1.0 + collection_bonus))
    
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
