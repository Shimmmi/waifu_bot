"""
Skill effects helper - fetch and aggregate active skill effects for users
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

logger = logging.getLogger(__name__)

try:
    from bot.models import User, UserSkillLevel, Skill
    SKILLS_AVAILABLE = True
except ImportError:
    SKILLS_AVAILABLE = False
    logger.warning("Skills models not available")


def get_user_skill_effects(db: Session, user_id: int) -> Dict[str, float]:
    """
    Fetch all active skill effects for a user.
    Returns a dictionary of effect_name -> total_value
    
    Example:
        {
            'gold_bonus': 0.2,
            'xp_bonus': 0.5,
            'summon_discount': 0.05
        }
    """
    if not SKILLS_AVAILABLE:
        return {}
    
    try:
        # Get user's skill levels
        skill_levels = db.query(UserSkillLevel).join(Skill).filter(
            UserSkillLevel.user_id == user_id
        ).all()
        
        effects = {}
        
        for skill_level in skill_levels:
            skill = skill_level.skill
            current_level = skill_level.level
            
            # Get effects for current level
            if current_level > 0 and str(current_level) in skill.effects:
                level_effects = skill.effects[str(current_level)]
                
                # Aggregate effects (for additive effects)
                for effect_name, effect_value in level_effects.items():
                    if effect_name not in effects:
                        effects[effect_name] = 0.0
                    effects[effect_name] += effect_value
        
        return effects
        
    except Exception as e:
        logger.error(f"❌ Error fetching skill effects for user {user_id}: {e}")
        return {}


def get_skill_effect_value(effects: Dict[str, float], effect_name: str, default: float = 0.0) -> float:
    """
    Get a specific effect value from the effects dictionary.
    
    Args:
        effects: Dictionary of effect_name -> value
        effect_name: Name of the effect to retrieve
        default: Default value if effect not found
    
    Returns:
        The effect value or default
    """
    return effects.get(effect_name, default)


def apply_skill_multiplier(base_value: float, multiplier: float) -> float:
    """
    Apply a skill multiplier to a base value.
    Multiplier is additive (e.g., 0.2 means +20%).
    
    Args:
        base_value: Original value
        multiplier: Skill multiplier (0.1 = +10%)
    
    Returns:
        Modified value
    """
    if multiplier <= 0:
        return base_value
    return base_value * (1 + multiplier)


def apply_skill_discount(base_value: float, discount: float) -> float:
    """
    Apply a skill discount to a base value.
    Discount is percentage (e.g., 0.05 means -5%).
    
    Args:
        base_value: Original value
        discount: Discount amount (0.05 = 5% off)
    
    Returns:
        Discounted value
    """
    if discount <= 0 or discount >= 1:
        return base_value
    return base_value * (1 - discount)


def apply_max_cap(value: float, cap_name: str, effects: Dict[str, float], default_cap: float = 10.0) -> float:
    """
    Apply a maximum cap to a value based on max_* effect.
    
    Args:
        value: Value to cap
        cap_name: Name of the max cap effect (e.g., 'max_collection_bonus')
        effects: Dictionary of effects
        default_cap: Default cap if not specified
    
    Returns:
        Capped value
    """
    cap = effects.get(cap_name, default_cap)
    return min(value, cap)

