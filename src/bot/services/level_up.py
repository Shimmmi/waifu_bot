"""
Level-up system for Waifu Bot
Handles XP thresholds, level progression, and stat increases
"""

import random
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LevelUpService:
    """Service for handling waifu level-ups"""
    
    @staticmethod
    def calculate_xp_for_next_level(current_level: int) -> int:
        """
        Calculate XP needed for next level
        Formula: XP = level * 100 (simple linear progression)
        
        Level 1 → 2: 100 XP
        Level 2 → 3: 200 XP
        Level 3 → 4: 300 XP
        etc.
        """
        return current_level * 100
    
    @staticmethod
    def get_total_xp_for_level(level: int) -> int:
        """
        Get total XP accumulated to reach a specific level
        This is the sum of all XP needed from level 1 to target level
        
        Level 1: 0 XP (starting point)
        Level 2: 100 XP
        Level 3: 300 XP (100 + 200)
        Level 4: 600 XP (100 + 200 + 300)
        etc.
        
        Formula: sum from 1 to (level-1) of (n * 100) = 50 * level * (level - 1)
        """
        if level <= 1:
            return 0
        return 50 * level * (level - 1)
    
    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """
        Calculate what level a waifu should be based on total XP
        """
        level = 1
        while True:
            xp_for_next = LevelUpService.get_total_xp_for_level(level + 1)
            if xp < xp_for_next:
                break
            level += 1
        return level
    
    @staticmethod
    def check_level_up(current_xp: int, current_level: int) -> tuple[bool, int]:
        """
        Check if waifu should level up based on current XP
        
        Returns:
            (should_level_up, new_level)
        """
        calculated_level = LevelUpService.calculate_level_from_xp(current_xp)
        should_level_up = calculated_level > current_level
        return should_level_up, calculated_level
    
    @staticmethod
    def select_random_stat_to_increase(stats: Dict[str, int]) -> str:
        """
        Randomly select a stat to increase on level up
        
        Available stats: power, charm, luck, affection, intellect, speed
        """
        stat_names = list(stats.keys())
        return random.choice(stat_names)
    
    @staticmethod
    def apply_level_up(
        waifu_data: Dict[str, Any],
        new_level: int
    ) -> Dict[str, Any]:
        """
        Apply level-up changes to waifu data
        
        Args:
            waifu_data: Dictionary with waifu info (stats, level, xp)
            new_level: The new level to set
            
        Returns:
            Dictionary with:
                - increased_stats: dict of {stat_name: increase_amount}
                - old_level: previous level
                - new_level: new level
                - old_stats: copy of stats before leveling
                - updated_stats: full updated stats dict
                - levels_gained: number of levels gained
        """
        old_level = waifu_data.get("level", 1)
        stats = dict(waifu_data.get("stats", {}))  # Make a copy
        old_stats = dict(stats)  # Save original stats
        
        # Calculate levels gained
        levels_gained = new_level - old_level
        
        # Track which stats increased and by how much
        stat_increases = {}
        
        # Increase one random stat for EACH level gained
        for i in range(levels_gained):
            random_stat = LevelUpService.select_random_stat_to_increase(stats)
            stats[random_stat] += 1
            stat_increases[random_stat] = stat_increases.get(random_stat, 0) + 1
            logger.info(f"Level {old_level + i} → {old_level + i + 1}: Increased {random_stat} by 1")
        
        logger.info(f"Total stat increases: {stat_increases}")
        
        return {
            "increased_stats": stat_increases,
            "old_level": old_level,
            "new_level": new_level,
            "old_stats": old_stats,
            "updated_stats": stats,
            "levels_gained": levels_gained
        }
    
    @staticmethod
    def format_level_up_message(
        waifu_name: str,
        level_up_info: Dict[str, Any]
    ) -> str:
        """
        Format a level-up notification message
        
        Args:
            waifu_name: Name of the waifu
            level_up_info: Info from apply_level_up()
            
        Returns:
            Formatted message string
        """
        stat_names_ru = {
            "power": "Сила",
            "charm": "Обаяние",
            "luck": "Удача",
            "affection": "Привязанность",
            "intellect": "Интеллект",
            "speed": "Скорость"
        }
        
        increased_stats = level_up_info["increased_stats"]
        old_stats = level_up_info["old_stats"]
        updated_stats = level_up_info["updated_stats"]
        new_level = level_up_info["new_level"]
        levels_gained = level_up_info.get("levels_gained", 1)
        
        # Calculate total power (sum of all stats)
        total_power = sum(updated_stats.values())
        
        # Build stat changes text
        stat_changes_lines = []
        for stat_name, increase_amount in increased_stats.items():
            stat_name_ru = stat_names_ru.get(stat_name, stat_name)
            old_value = old_stats[stat_name]
            new_value = updated_stats[stat_name]
            stat_changes_lines.append(f"📈 <b>{stat_name_ru}</b>: {old_value} → {new_value} (+{increase_amount})")
        
        stat_changes_text = "\n".join(stat_changes_lines)
        
        if levels_gained > 1:
            message = (
                f"🎉 <b>ПОВЫШЕНИЕ УРОВНЯ!</b> 🎉\n\n"
                f"🌟 <b>{waifu_name}</b> достигла <b>{new_level} уровня</b>! "
                f"(+{levels_gained} уровней)\n\n"
                f"{stat_changes_text}\n\n"
                f"💪 <b>Общая сила</b>: {total_power}\n\n"
                f"✨ Поздравляем с прогрессом!"
            )
        else:
            message = (
                f"🎉 <b>ПОВЫШЕНИЕ УРОВНЯ!</b> 🎉\n\n"
                f"🌟 <b>{waifu_name}</b> достигла <b>{new_level} уровня</b>!\n\n"
                f"{stat_changes_text}\n\n"
                f"💪 <b>Общая сила</b>: {total_power}\n\n"
                f"✨ Продолжай в том же духе!"
            )
        
        return message
    
    @staticmethod
    def get_xp_progress_info(current_xp: int, current_level: int) -> Dict[str, Any]:
        """
        Get information about XP progress for current level
        
        Returns:
            Dictionary with:
                - current_xp: Current total XP
                - current_level: Current level
                - xp_for_current_level: Total XP needed to reach current level
                - xp_for_next_level: Total XP needed to reach next level
                - xp_in_current_level: XP progress within current level
                - xp_needed_for_next: XP still needed for next level
                - progress_percentage: Progress % towards next level
        """
        xp_for_current = LevelUpService.get_total_xp_for_level(current_level)
        xp_for_next = LevelUpService.get_total_xp_for_level(current_level + 1)
        
        xp_in_current_level = current_xp - xp_for_current
        xp_needed_for_next = xp_for_next - current_xp
        xp_needed_in_level = xp_for_next - xp_for_current
        
        progress_percentage = (xp_in_current_level / xp_needed_in_level * 100) if xp_needed_in_level > 0 else 0
        
        return {
            "current_xp": current_xp,
            "current_level": current_level,
            "xp_for_current_level": xp_for_current,
            "xp_for_next_level": xp_for_next,
            "xp_in_current_level": xp_in_current_level,
            "xp_needed_for_next": xp_needed_for_next,
            "xp_needed_in_level": xp_needed_in_level,
            "progress_percentage": round(progress_percentage, 1)
        }


# Global instance
level_up_service = LevelUpService()

