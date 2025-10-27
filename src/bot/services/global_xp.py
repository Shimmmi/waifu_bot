"""
Global Account XP System

Handles user account leveling system with automatic level-ups and skill points.
"""

import asyncio
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Any
import logging

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from bot.config import get_settings
from bot.models import User

logger = logging.getLogger(__name__)


class GlobalXPService:
    # XP rates per action type
    XP_RATES = {
        "text": 1,           # Text message >=5 chars
        "media": 2,          # Image/sticker
        "link": 5,           # Link/video
        "voice": 3,          # Voice message
        "reaction": 0.5,     # Reaction/like (accumulated)
    }
    
    DAILY_XP_CAP = 500
    RATE_LIMIT_SECONDS = 30
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: redis.Redis | None = None
    
    async def get_redis(self) -> redis.Redis:
        """Get Redis client, create if needed."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(self.settings.redis_url)
        return self.redis_client
    
    async def close_redis(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    def calculate_xp_for_message(self, message_type: str, text_length: int = 0) -> int:
        """Calculate XP based on message type and content."""
        if message_type == "text":
            return self.XP_RATES["text"] if text_length >= 5 else 0
        return self.XP_RATES.get(message_type, 0)
    
    async def is_rate_limited(self, user_id: int) -> bool:
        """Check if user is rate limited (max 1 XP per user every 30 seconds)."""
        try:
            redis_client = await self.get_redis()
            key = f"xp_rate_limit:{user_id}"
            
            exists = await redis_client.exists(key)
            if exists:
                return True  # Rate limited
            
            # Set rate limit with 30 second TTL
            await redis_client.setex(key, self.RATE_LIMIT_SECONDS, "1")
            return False
        except Exception as e:
            # Log error but don't fail - allow XP to be awarded
            # This prevents Redis issues from breaking the XP system
            logger.warning(f"Rate limit check failed (Redis issue): {e}. Allowing XP award.")
            return False  # Don't block if Redis fails
    
    def get_xp_required_for_level(self, level: int) -> int:
        """Calculate XP required for a specific level using formula: 100 * level^1.1"""
        return int(100 * (level ** 1.1))
    
    def get_total_xp_for_level(self, level: int) -> int:
        """Calculate total XP accumulated to reach a specific level."""
        total = 0
        for lvl in range(1, level + 1):
            total += self.get_xp_required_for_level(lvl)
        return total
    
    def calculate_level_from_xp(self, xp: int) -> int:
        """Calculate current level from total XP."""
        level = 1
        while xp >= self.get_total_xp_for_level(level + 1):
            level += 1
        return level
    
    def check_level_up(self, current_level: int, new_xp: int) -> tuple[bool, int]:
        """
        Check if user should level up with new XP.
        Returns (should_level_up, new_level)
        """
        new_level = self.calculate_level_from_xp(new_xp)
        should_level_up = new_level > current_level
        return should_level_up, new_level
    
    def calculate_skill_points_from_levels(self, start_level: int, end_level: int) -> int:
        """Calculate skill points gained from leveling up."""
        return end_level - start_level
    
    async def award_global_xp(
        self,
        session: Session,
        user_id: int,
        xp_amount: int,
        source: str = "message",
        meta: dict[str, Any] | None = None,
        skip_rate_limit: bool = False,
    ) -> dict[str, Any]:
        """
        Award global XP to user account.
        Returns dict with level_up info if leveled up.
        
        Args:
            session: Database session
            user_id: Database user ID
            xp_amount: Amount of XP to award
            source: Source of XP (e.g., "message")
            meta: Additional metadata
            skip_rate_limit: If True, skip rate limit check (already done externally)
        """
        if xp_amount <= 0:
            return {"level_up": False}
        
        # Get user
        result = session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User {user_id} not found")
            return {"level_up": False}
        
        # Check daily XP cap
        if user.daily_xp >= self.DAILY_XP_CAP:
            logger.info(f"User {user_id} reached daily XP cap")
            return {"level_up": False, "daily_cap_reached": True}
        
        # Check if we need to reset daily XP (next day)
        # Handle timezone-aware and timezone-naive datetimes
        now = datetime.utcnow()
        last_reset = user.last_xp_reset
        
        # Make both datetimes timezone-aware or both naive for comparison
        if last_reset.tzinfo is not None and now.tzinfo is None:
            # last_reset is aware, now is naive - make now aware
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        elif last_reset.tzinfo is None and now.tzinfo is not None:
            # last_reset is naive, now is aware - make now naive
            now = now.replace(tzinfo=None)
        
        time_since_reset = now - last_reset
        if time_since_reset >= timedelta(days=1):
            # Reset daily XP
            user.daily_xp = 0
            user.last_xp_reset = now
            logger.info(f"Reset daily XP for user {user_id}")
        
        # Check daily XP cap
        remaining_daily_xp = self.DAILY_XP_CAP - user.daily_xp
        actual_xp = min(xp_amount, remaining_daily_xp)
        
        # Update global XP and daily XP
        old_level = user.account_level
        user.global_xp += actual_xp
        user.daily_xp += actual_xp
        # Ensure last_global_xp is set properly based on now's timezone
        if now.tzinfo is None:
            from datetime import timezone
            user.last_global_xp = now.replace(tzinfo=timezone.utc)
        else:
            user.last_global_xp = now
        
        # Check for level up
        should_level_up, new_level = self.check_level_up(user.account_level, user.global_xp)
        
        if should_level_up:
            # Calculate skill points gained
            skill_points_gained = self.calculate_skill_points_from_levels(old_level, new_level)
            user.account_level = new_level
            user.skill_points += skill_points_gained
            
            logger.info(
                f"🎉 User {user_id} leveled up! "
                f"Level {old_level} → {new_level} (+{skill_points_gained} skill points)"
            )
            
            session.commit()
            
            return {
                "level_up": True,
                "old_level": old_level,
                "new_level": new_level,
                "skill_points_gained": skill_points_gained,
                "total_skill_points": user.skill_points,
                "global_xp": user.global_xp,
                "daily_xp": user.daily_xp
            }
        
        session.commit()
        
        return {
            "level_up": False,
            "global_xp": user.global_xp,
            "daily_xp": user.daily_xp
        }


# Global XP service instance
global_xp_service = GlobalXPService()
