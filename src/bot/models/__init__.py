"""
Models package for Waifu Bot
"""

# Import Base first to avoid circular imports
from bot.models import Base

# Then import skill models
try:
    from bot.models.skills import UserSkills, Skill, UserSkillLevel, SkillPointEarning
except ImportError:
    # If skills module doesn't exist yet, define empty classes
    UserSkills = None
    Skill = None
    UserSkillLevel = None
    SkillPointEarning = None

__all__ = [
    'Base',
    'UserSkills',
    'Skill',
    'UserSkillLevel',
    'SkillPointEarning',
]
