import random
from typing import Dict, List, Tuple, Optional, Any
from ..data_tables import EVENTS


def calculate_event_score(waifu: Dict, event_type: str, user_id: Optional[int] = None, session: Optional[Any] = None) -> Tuple[float, str]:
    """Вычисляет очки вайфу в событии с учетом всех факторов"""
    if event_type not in EVENTS:
        return 0.0, "Неизвестное событие"
    
    event = EVENTS[event_type]
    stats = waifu.get("stats", {})
    dynamic = waifu.get("dynamic", {})
    
    # Базовые очки из характеристик
    base_score = 0
    for stat in event["base_stats"]:
        if stat in stats:
            # Добавляем случайность для реализма
            multiplier = random.uniform(0.8, 1.2)
            base_score += stats[stat] * multiplier
    
    # Бонус за профессию
    profession_bonus = 1.0
    profession_bonus_name = event.get("profession_bonus")
    if profession_bonus_name and waifu.get("profession") == profession_bonus_name:
        profession_bonus = 1.25
    
    # Бонусы от динамических характеристик
    mood_bonus = dynamic.get("mood", 50) / 100
    loyalty_bonus = dynamic.get("loyalty", 50) / 100
    
    # Бонус за соответствие фильтру (для race/profession/nationality событий)
    filter_bonus = 1.0
    filter_type = event.get("filter_type", "none")
    if filter_type == "race" and waifu.get("race") == event.get("filter_value"):
        filter_bonus = 1.15  # +15% за правильную расу
    elif filter_type == "profession" and waifu.get("profession") == event.get("filter_value"):
        filter_bonus = 1.15  # +15% за правильную профессию
    elif filter_type == "nationality" and waifu.get("nationality") == event.get("filter_value"):
        filter_bonus = 1.15  # +15% за правильную национальность
    elif filter_type == "rarity":
        # Бонус за редкость: выше редкость = выше бонус
        rarity_multipliers = {
            "Common": 1.0,
            "Uncommon": 1.1,
            "Rare": 1.2,
            "Epic": 1.3,
            "Legendary": 1.5
        }
        filter_bonus = rarity_multipliers.get(waifu.get("rarity"), 1.0)
    
    # Бонус за уровень
    level = waifu.get("level", 1)
    level_bonus = 1.0 + (level - 1) * 0.02  # +2% за каждый уровень выше 1
    
    # Итоговый счет
    final_score = (
        base_score 
        * profession_bonus 
        * filter_bonus
        * level_bonus
        * (0.8 + mood_bonus * 0.2) 
        * (0.9 + loyalty_bonus * 0.1)
    )
    
    # Добавляем случайность для интереса
    final_score *= random.uniform(0.9, 1.1)
    
    return round(final_score, 2), event["name"]


def filter_waifus_for_event(waifus: List[Any], event_config: Dict, user_id: Optional[int] = None, session: Optional[Any] = None) -> List[Any]:
    """
    Фильтрует список вайфу в соответствии с требованиями события
    
    Args:
        waifus: Список всех вайфу игрока
        event_config: Конфигурация события из EVENTS
        user_id: ID пользователя (опционально, для расчета мощи)
        session: SQLAlchemy сессия (опционально, для расчета мощи)
        
    Returns:
        Отфильтрованный список вайфу
    """
    filtered = list(waifus)
    
    filter_type = event_config.get("filter_type", "none")
    filter_value = event_config.get("filter_value")
    
    if filter_type == "race":
        filtered = [w for w in filtered if w.race == filter_value]
    elif filter_type == "profession":
        filtered = [w for w in filtered if w.profession == filter_value]
    elif filter_type == "nationality":
        filtered = [w for w in filtered if w.nationality == filter_value]
    elif filter_type == "rarity":
        rarity_order = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
        min_rarity_index = rarity_order.index(filter_value) if filter_value in rarity_order else 0
        filtered = [
            w for w in filtered 
            if w.rarity in rarity_order and rarity_order.index(w.rarity) >= min_rarity_index
        ]
    # filter_type == "none" или "primary_stat" - без фильтрации
    
    return filtered


def sort_waifus_for_event(waifus: List[Any], event_config: Dict, user_id: Optional[int] = None, session: Optional[Any] = None) -> List[Any]:
    """
    Сортирует вайфу для отображения в порядке выбора
    
    Args:
        waifus: Список отфильтрованных вайфу
        event_config: Конфигурация события
        user_id: ID пользователя (для расчета мощи)
        session: SQLAlchemy сессия (для расчета мощи)
        
    Returns:
        Отсортированный список вайфу (от лучшего к худшему)
    """
    sort_by = event_config.get("sort_by", "power")
    
    def get_sort_key(waifu: Any) -> float:
        if sort_by == "power":
            # Общая мощь вайфу
            try:
                from bot.services.waifu_generator import calculate_waifu_power
                from bot.services.skill_effects import get_user_skill_effects
                
                skill_effects = {}
                if user_id is not None and session is not None:
                    try:
                        skill_effects = get_user_skill_effects(session, user_id)
                    except Exception:
                        pass
                
                return calculate_waifu_power({
                    "stats": waifu.stats,
                    "dynamic": waifu.dynamic,
                    "level": waifu.level,
                    "rarity": waifu.rarity
                }, skill_effects)
            except Exception:
                # Fallback: simple sum of stats
                stats = waifu.stats if hasattr(waifu, 'stats') else {}
                return sum(stats.values()) if isinstance(stats, dict) else 0
        
        elif sort_by == "power_stat":
            stats = waifu.stats if hasattr(waifu, 'stats') else {}
            return stats.get("power", 0) if isinstance(stats, dict) else 0
        elif sort_by == "charm_stat":
            stats = waifu.stats if hasattr(waifu, 'stats') else {}
            return stats.get("charm", 0) if isinstance(stats, dict) else 0
        elif sort_by == "intellect_stat":
            stats = waifu.stats if hasattr(waifu, 'stats') else {}
            return stats.get("intellect", 0) if isinstance(stats, dict) else 0
        elif sort_by == "speed_stat":
            stats = waifu.stats if hasattr(waifu, 'stats') else {}
            return stats.get("speed", 0) if isinstance(stats, dict) else 0
        elif sort_by == "luck_stat":
            stats = waifu.stats if hasattr(waifu, 'stats') else {}
            return stats.get("luck", 0) if isinstance(stats, dict) else 0
        elif sort_by == "affection_stat":
            stats = waifu.stats if hasattr(waifu, 'stats') else {}
            return stats.get("affection", 0) if isinstance(stats, dict) else 0
        else:
            # По умолчанию по общей мощи
            try:
                from bot.services.waifu_generator import calculate_waifu_power
                return calculate_waifu_power({
                    "stats": waifu.stats,
                    "dynamic": waifu.dynamic,
                    "level": waifu.level,
                    "rarity": waifu.rarity
                }, {})
            except Exception:
                return 0
    
    sorted_waifus = sorted(waifus, key=get_sort_key, reverse=True)
    return sorted_waifus


def get_event_rewards(score: float, event_type: str) -> Dict:
    """Вычисляет награды за событие"""
    base_rewards = {
        "dance": {"coins": 20, "xp": 15},
        "hunt": {"coins": 30, "xp": 20},
        "quiz": {"coins": 25, "xp": 18},
        "cooking": {"coins": 22, "xp": 16},
        "singing": {"coins": 28, "xp": 19}
    }
    
    base = base_rewards.get(event_type, {"coins": 20, "xp": 15})
    
    # Множитель на основе очков
    if score >= 100:
        multiplier = 2.0
    elif score >= 80:
        multiplier = 1.5
    elif score >= 60:
        multiplier = 1.2
    else:
        multiplier = 1.0
    
    return {
        "coins": int(base["coins"] * multiplier),
        "xp": int(base["xp"] * multiplier),
        "score": score
    }


def get_random_event() -> str:
    """Возвращает случайное событие"""
    return random.choice(list(EVENTS.keys()))


def get_event_description(event_type: str) -> str:
    """Возвращает описание события"""
    if event_type in EVENTS:
        event = EVENTS[event_type]
        return f"🎯 <b>{event['name']}</b>\n{event['description']}"
    return "Неизвестное событие"


def format_event_result(waifu: Dict, event_type: str, score: float, rewards: Dict) -> str:
    """Форматирует результат события"""
    event_name = EVENTS.get(event_type, {}).get("name", "Событие")
    
    result = f"""
🎯 <b>Результат события: {event_name}</b>

👤 <b>{waifu['name']}</b> участвовала в событии!
📊 Очки: {score}
🏆 Результат: {get_performance_text(score)}

💰 <b>Награды:</b>
🪙 Монеты: +{rewards['coins']}
⭐ Опыт: +{rewards['xp']}

💭 <b>Влияние на вайфу:</b>
⚡ Энергия: -20
😊 Настроение: +5
💝 Лояльность: +2
"""
    
    return result.strip()


def get_performance_text(score: float) -> str:
    """Возвращает текстовое описание результата"""
    if score >= 100:
        return "🏆 Превосходно!"
    elif score >= 80:
        return "🥇 Отлично!"
    elif score >= 60:
        return "🥈 Хорошо"
    elif score >= 40:
        return "🥉 Удовлетворительно"
    else:
        return "😔 Нужно тренироваться"


def get_available_events() -> List[Dict]:
    """Возвращает список доступных событий"""
    events = []
    for event_type, event_data in EVENTS.items():
        events.append({
            "id": event_type,
            "name": event_data["name"],
            "description": event_data["description"],
            "base_stats": event_data["base_stats"],
            "profession_bonus": event_data["profession_bonus"]
        })
    return events


def can_participate_in_event(
    waifu: Dict, 
    event_type: str, 
    user_id: Optional[int] = None, 
    session: Optional[Any] = None
) -> Tuple[bool, str]:
    """
    Проверяет, может ли вайфу участвовать в событии.
    
    Args:
        waifu: Словарь с данными вайфу
        event_type: Тип события
        user_id: ID пользователя (опционально, для учета навыка endurance)
        session: SQLAlchemy сессия (опционально, для учета навыка endurance)
    
    Returns:
        Кортеж (может_участвовать: bool, причина: str)
    """
    if event_type not in EVENTS:
        return False, "Неизвестное событие"
    
    # Определяем минимальную требуемую энергию
    min_energy_required = 20  # Базовая стоимость
    
    # Если передан user_id и session, учитываем навык endurance
    if user_id is not None and session is not None:
        try:
            from bot.services.energy_cost import get_min_energy_required
            min_energy_required = get_min_energy_required(user_id, session, base_cost=20)
        except Exception:
            # Если ошибка, используем базовую стоимость
            pass
    
    # Проверяем энергию
    energy = waifu.get("dynamic", {}).get("energy", 0)
    if energy < min_energy_required:
        return False, f"Недостаточно энергии для участия (требуется {min_energy_required})"
    
    # Проверяем настроение
    mood = waifu.get("dynamic", {}).get("mood", 0)
    if mood < 30:
        return False, "Слишком плохое настроение для участия"
    
    return True, "Может участвовать"
