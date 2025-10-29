"""
Skill points earning system
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from bot.models import User
from bot.models.skills import UserSkills, SkillPointEarning

logger = logging.getLogger(__name__)


def earn_skill_points(
    db: Session, 
    user_id: int, 
    points: int, 
    source: str, 
    source_details: Optional[Dict[str, Any]] = None
) -> bool:
    """Earn skill points for user"""
    try:
        # Get or create user skills record
        user_skills = db.query(UserSkills).filter(UserSkills.user_id == user_id).first()
        if not user_skills:
            user_skills = UserSkills(user_id=user_id, skill_points=0, total_earned_points=0)
            db.add(user_skills)
        
        # Add points
        user_skills.skill_points += points
        user_skills.total_earned_points += points
        
        # Record earning
        earning = SkillPointEarning(
            user_id=user_id,
            points_earned=points,
            source=source,
            source_details=source_details or {}
        )
        db.add(earning)
        
        db.commit()
        
        logger.info(f"✅ User {user_id} earned {points} skill points from {source}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error earning skill points: {e}", exc_info=True)
        db.rollback()
        return False


def calculate_chat_message_points(user: User, message_length: int = 0) -> int:
    """Calculate skill points for chat message"""
    base_points = 1
    
    # Bonus for longer messages
    if message_length > 50:
        base_points += 1
    if message_length > 100:
        base_points += 1
    if message_length > 200:
        base_points += 1
    
    # Bonus for account level
    level_bonus = user.account_level // 10  # +1 point per 10 levels
    
    return base_points + level_bonus


def calculate_daily_bonus_points(user: User) -> int:
    """Calculate skill points for daily bonus"""
    base_points = 5
    
    # Bonus for streak
    streak_bonus = min(user.daily_streak // 7, 10)  # +1 point per week, max 10
    
    return base_points + streak_bonus


def calculate_waifu_summon_points(waifu_count: int, rarity: str) -> int:
    """Calculate skill points for waifu summoning"""
    base_points = waifu_count  # 1 point per waifu
    
    # Rarity bonus
    rarity_multipliers = {
        'Common': 1,
        'Uncommon': 2,
        'Rare': 3,
        'Epic': 5,
        'Legendary': 10
    }
    
    rarity_bonus = rarity_multipliers.get(rarity, 1)
    return base_points * rarity_bonus


def calculate_waifu_upgrade_points(xp_gained: int) -> int:
    """Calculate skill points for waifu upgrade"""
    return max(1, xp_gained // 100)  # 1 point per 100 XP gained


def get_user_skill_effects(db: Session, user_id: int) -> Dict[str, float]:
    """Get all active skill effects for user"""
    try:
        from bot.models.skills import UserSkillLevel, Skill
        
        # Get user's skill levels
        skill_levels = db.query(UserSkillLevel).join(Skill).filter(
            UserSkillLevel.user_id == user_id
        ).all()
        
        effects = {}
        for skill_level in skill_levels:
            skill = skill_level.skill
            current_level = skill_level.level
            
            if current_level > 0 and str(current_level) in skill.effects:
                level_effects = skill.effects[str(current_level)]
                for effect_name, effect_value in level_effects.items():
                    if effect_name not in effects:
                        effects[effect_name] = 0
                    effects[effect_name] += effect_value
        
        return effects
        
    except Exception as e:
        logger.error(f"❌ Error getting skill effects: {e}", exc_info=True)
        return {}


def apply_skill_effects_to_waifu(waifu_data: Dict[str, Any], skill_effects: Dict[str, float]) -> Dict[str, Any]:
    """Apply skill effects to waifu data"""
    try:
        # Apply power bonuses
        if 'power_bonus' in skill_effects:
            power_multiplier = 1 + skill_effects['power_bonus']
            if 'stats' in waifu_data and 'power' in waifu_data['stats']:
                waifu_data['stats']['power'] = int(waifu_data['stats']['power'] * power_multiplier)
        
        # Apply individual stat bonuses
        stat_bonuses = {
            'intellect_bonus': 'intellect',
            'charm_bonus': 'charm',
            'dexterity_bonus': 'bond',  # bond is dexterity in dynamic
            'luck_bonus': 'luck',
            'speed_bonus': 'speed'
        }
        
        for bonus_key, stat_key in stat_bonuses.items():
            if bonus_key in skill_effects:
                multiplier = 1 + skill_effects[bonus_key]
                if 'stats' in waifu_data and stat_key in waifu_data['stats']:
                    waifu_data['stats'][stat_key] = int(waifu_data['stats'][stat_key] * multiplier)
                elif 'dynamic' in waifu_data and stat_key in waifu_data['dynamic']:
                    waifu_data['dynamic'][stat_key] = int(waifu_data['dynamic'][stat_key] * multiplier)
        
        # Apply rarity-specific bonuses
        if 'rare_power_bonus' in skill_effects and waifu_data.get('rarity') in ['Rare', 'Epic', 'Legendary']:
            power_multiplier = 1 + skill_effects['rare_power_bonus']
            if 'stats' in waifu_data and 'power' in waifu_data['stats']:
                waifu_data['stats']['power'] = int(waifu_data['stats']['power'] * power_multiplier)
        
        if 'epic_power_bonus' in skill_effects and waifu_data.get('rarity') in ['Epic', 'Legendary']:
            power_multiplier = 1 + skill_effects['epic_power_bonus']
            if 'stats' in waifu_data and 'power' in waifu_data['stats']:
                waifu_data['stats']['power'] = int(waifu_data['stats']['power'] * power_multiplier)
        
        return waifu_data
        
    except Exception as e:
        logger.error(f"❌ Error applying skill effects: {e}", exc_info=True)
        return waifu_data
