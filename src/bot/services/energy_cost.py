"""
Energy cost calculation with endurance skill support
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from bot.services.skill_effects import get_user_skill_effects

logger = logging.getLogger(__name__)


def calculate_energy_cost(base_cost: int, user_id: int, session: Session) -> int:
    """
    Рассчитывает стоимость энергии с учетом навыка 'endurance'.
    
    Args:
        base_cost: Базовая стоимость энергии (например, 20)
        user_id: ID пользователя
        session: SQLAlchemy сессия
        
    Returns:
        Финальная стоимость энергии (минимум 1)
    """
    try:
        skill_effects = get_user_skill_effects(session, user_id)
        energy_cost_reduction = skill_effects.get('energy_cost_reduction', 0.0)
        
        if energy_cost_reduction > 0:
            # Применяем скидку (0.2 = -20%, 0.4 = -40%, 0.6 = -60%)
            reduced_cost = int(base_cost * (1.0 - energy_cost_reduction))
            final_cost = max(1, reduced_cost)  # Минимум 1 энергия
            
            logger.info(f"💪 Endurance skill applied for user {user_id}: "
                       f"{energy_cost_reduction*100:.0f}% reduction, "
                       f"energy cost: {base_cost} → {final_cost}")
            
            return final_cost
        
        return base_cost
        
    except Exception as e:
        logger.error(f"❌ Error calculating energy cost for user {user_id}: {e}")
        return base_cost


def get_min_energy_required(user_id: int, session: Session, base_cost: int = 20) -> int:
    """
    Возвращает минимальную энергию для участия в событии с учетом навыка 'endurance'.
    
    Args:
        user_id: ID пользователя
        session: SQLAlchemy сессия
        base_cost: Базовая стоимость (по умолчанию 20)
        
    Returns:
        Минимальная требуемая энергия
    """
    return calculate_energy_cost(base_cost, user_id, session)
