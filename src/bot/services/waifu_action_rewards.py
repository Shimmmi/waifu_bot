"""
Waifu action rewards calculation with golden_hand skill support
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from bot.services.skill_effects import get_user_skill_effects

logger = logging.getLogger(__name__)


def apply_waifu_gold_bonus(base_gold: int, user_id: int, session: Session) -> int:
    """
    Применяет бонус 'golden_hand' к золоту от действий вайфу.
    
    Args:
        base_gold: Базовое количество золота
        user_id: ID пользователя
        session: SQLAlchemy сессия
        
    Returns:
        Финальное количество золота с учетом бонуса
    """
    try:
        skill_effects = get_user_skill_effects(session, user_id)
        waifu_gold_bonus = skill_effects.get('waifu_gold_bonus', 0.0)
        
        if waifu_gold_bonus > 0:
            bonus_gold = int(base_gold * waifu_gold_bonus)
            final_gold = base_gold + bonus_gold
            
            logger.info(f"🤲 Golden Hand skill applied for user {user_id}: "
                       f"+{waifu_gold_bonus*100:.0f}%, "
                       f"gold: {base_gold} → {final_gold}")
            
            return final_gold
        
        return base_gold
        
    except Exception as e:
        logger.error(f"❌ Error applying waifu gold bonus for user {user_id}: {e}")
        return base_gold
