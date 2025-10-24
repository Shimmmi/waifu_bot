import random
from typing import Dict, List, Tuple
from ..data_tables import EVENTS


def calculate_event_score(waifu: Dict, event_type: str) -> Tuple[float, str]:
    """Вычисляет очки вайфу в событии"""
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
    if waifu.get("profession") == event["profession_bonus"]:
        profession_bonus = 1.25
    
    # Бонусы от динамических характеристик
    mood_bonus = dynamic.get("mood", 50) / 100
    loyalty_bonus = dynamic.get("loyalty", 50) / 100
    
    # Итоговый счет
    final_score = base_score * profession_bonus * (0.8 + mood_bonus * 0.2) * (0.9 + loyalty_bonus * 0.1)
    
    # Добавляем случайность для интереса
    final_score *= random.uniform(0.9, 1.1)
    
    return round(final_score, 2), event["name"]


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


def can_participate_in_event(waifu: Dict, event_type: str) -> Tuple[bool, str]:
    """Проверяет, может ли вайфу участвовать в событии"""
    if event_type not in EVENTS:
        return False, "Неизвестное событие"
    
    # Проверяем энергию
    energy = waifu.get("dynamic", {}).get("energy", 0)
    if energy < 20:
        return False, "Недостаточно энергии для участия"
    
    # Проверяем настроение
    mood = waifu.get("dynamic", {}).get("mood", 0)
    if mood < 30:
        return False, "Слишком плохое настроение для участия"
    
    return True, "Может участвовать"
