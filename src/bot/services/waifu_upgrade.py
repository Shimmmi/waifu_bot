"""
Waifu Upgrade and Teaching System

Handles waifu leveling limits, upgrades, and the teaching system where players
can sacrifice waifus to give XP to other waifus.
"""

import math
from typing import Any

from bot.services.waifu_generator import calculate_waifu_power
from bot.services.level_up import LevelUpService


# Max level per rarity
MAX_LEVELS = {
    "Common": 30,
    "Uncommon": 35,
    "Rare": 40,
    "Epic": 45,
    "Legendary": 50,
}

# Rarity multipliers for XP calculation in teaching system
RARITY_RATIOS = {
    "Common": 1.0,
    "Uncommon": 1.5,
    "Rare": 2.0,
    "Epic": 3.0,
    "Legendary": 5.0,
}

# Upgrade requirements: merge 2 max level waifus of same rarity
UPGRADE_REQUIREMENTS = {
    "Common": {"target_rarity": "Uncommon", "required_count": 2, "required_level": 30},
    "Uncommon": {"target_rarity": "Rare", "required_count": 2, "required_level": 35},
    "Rare": {"target_rarity": "Epic", "required_count": 2, "required_level": 40},
    "Epic": {"target_rarity": "Legendary", "required_count": 2, "required_level": 45},
}


def get_max_level(rarity: str) -> int:
    """Get max level for a specific rarity."""
    return MAX_LEVELS.get(rarity, 30)


def get_rarity_ratio(rarity: str) -> float:
    """Get XP multiplier for a specific rarity."""
    return RARITY_RATIOS.get(rarity, 1.0)


def calculate_teaching_xp(
    student_level: int, 
    teacher_rarity: str, 
    teacher_level: int, 
    teacher_xp: int
) -> int:
    """
    Calculate XP given when a waifu teaches another.
    
    Formula: (XP needed for teacher's current level * rarity ratio) / 2
    
    Args:
        student_level: Current level of the waifu receiving XP
        teacher_rarity: Rarity of the waifu being sacrificed
        teacher_level: Level of the waifu being sacrificed  
        teacher_xp: Current XP of the waifu being sacrificed
    
    Returns:
        Amount of XP to award
    """
    # Calculate XP the teacher would need for their next level from their current level
    if teacher_level > 0:
        # Calculate cumulative XP to reach teacher's current level
        cumulative_xp = sum(
            LevelUpService.calculate_xp_for_next_level(level)
            for level in range(1, teacher_level + 1)
        )
        # Use teacher's XP value instead (their earned XP)
        teacher_total_xp = cumulative_xp + teacher_xp
    else:
        teacher_total_xp = teacher_xp
    
    # Get teacher's rarity ratio
    ratio = get_rarity_ratio(teacher_rarity)
    
    # Calculate base XP based on teacher's total accumulated XP
    base_xp = teacher_total_xp * ratio
    
    # Divide by 2 as specified
    xp_awarded = int(base_xp / 2)
    
    return max(1, xp_awarded)  # Minimum 1 XP


def can_upgrade(rarity: str, waifus_list: list[dict]) -> bool:
    """
    Check if player has enough waifus to perform an upgrade.
    
    Args:
        rarity: Source rarity to upgrade from
        waifus_list: List of waifu dictionaries with 'level' and 'rarity'
    
    Returns:
        True if upgrade is possible
    """
    if rarity not in UPGRADE_REQUIREMENTS:
        return False  # Legendary is max
    
    req = UPGRADE_REQUIREMENTS[rarity]
    max_level = get_max_level(rarity)
    
    # Count waifus that match requirements (max level of specified rarity)
    matching_count = sum(
        1 for w in waifus_list 
        if w.get('rarity') == rarity and w.get('level') == max_level
    )
    
    return matching_count >= req['required_count']


def get_upgrade_target(rarity: str) -> str | None:
    """Get the target rarity when upgrading from a given rarity."""
    if rarity in UPGRADE_REQUIREMENTS:
        return UPGRADE_REQUIREMENTS[rarity]["target_rarity"]
    return None


def perform_upgrade(
    waifus: list[dict],
    rarity: str
) -> dict[str, Any]:
    """
    Perform an upgrade by consuming max level waifus.
    
    Args:
        waifus: List of waifu dictionaries to upgrade from
        rarity: Source rarity
        
    Returns:
        Dict with 'success', 'consumed_ids', and 'new_waifu_data' if successful
    """
    if not can_upgrade(rarity, waifus):
        return {"success": False, "error": "Not enough waifus to upgrade"}
    
    req = UPGRADE_REQUIREMENTS[rarity]
    
    # Find waifus to consume
    to_consume = [
        w for w in waifus
        if w.get('rarity') == rarity and w.get('level') == req['required_level']
    ][:req['required_count']]
    
    consumed_ids = [w['id'] for w in to_consume]
    
    # Create new waifu data
    new_waifu_data = {
        'rarity': req['target_rarity'],
        'level': 1,
        'xp': 0,
        # Use stats from first consumed waifu as base
        'stats': to_consume[0].get('stats', {}),
    }
    
    return {
        "success": True,
        "consumed_ids": consumed_ids,
        "new_waifu_data": new_waifu_data
    }
