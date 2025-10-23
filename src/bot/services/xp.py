import asyncio
from datetime import datetime, timedelta
from typing import Any

import redis.asyncio as redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import get_settings
from bot.models import User, WaifuInstance, XPLog


class XPService:
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
        """Check if user is rate limited."""
        redis_client = await self.get_redis()
        key = f"xp_rate_limit:{user_id}"
        
        # Check if key exists (rate limit active)
        exists = await redis_client.exists(key)
        if exists:
            return True
        
        # Set rate limit for 30 seconds
        await redis_client.setex(key, self.RATE_LIMIT_SECONDS, "1")
        return False
    
    async def get_daily_xp_remaining(self, session: AsyncSession, user_id: int) -> int:
        """Get remaining daily XP for user."""
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return 0
        
        # Reset daily XP if it's a new day
        now = datetime.utcnow()
        last_reset = user.last_xp_reset.replace(tzinfo=None)
        
        if now.date() > last_reset.date():
            # New day, reset daily XP
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(daily_xp=0, last_xp_reset=now)
            )
            await session.commit()
            return self.DAILY_XP_CAP
        
        return max(0, self.DAILY_XP_CAP - user.daily_xp)
    
    async def get_active_waifu(self, session: AsyncSession, user_id: int) -> WaifuInstance | None:
        """Get user's active waifu for XP distribution."""
        result = await session.execute(
            select(WaifuInstance)
            .where(WaifuInstance.owner_id == user_id)
            .where(WaifuInstance.is_active == True)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def award_xp(
        self,
        session: AsyncSession,
        user_id: int,
        xp_amount: int,
        source: str = "message",
        meta: dict[str, Any] | None = None,
    ) -> bool:
        """Award XP to user's active waifu."""
        if xp_amount <= 0:
            return False
        
        # Check rate limit
        if await self.is_rate_limited(user_id):
            return False
        
        # Check daily XP cap
        remaining_xp = await self.get_daily_xp_remaining(session, user_id)
        if remaining_xp <= 0:
            return False
        
        # Limit XP to remaining daily amount
        actual_xp = min(xp_amount, remaining_xp)
        
        # Get active waifu
        waifu = await self.get_active_waifu(session, user_id)
        if not waifu:
            # No active waifu, still log but don't award XP
            xp_log = XPLog(
                user_id=user_id,
                waifu_id=None,
                source=source,
                amount=actual_xp,
                meta=meta,
            )
            session.add(xp_log)
            await session.commit()
            return False
        
        # Award XP to waifu
        new_xp = waifu.xp + actual_xp
        new_level = self.calculate_level_from_xp(new_xp)
        
        # Update waifu
        await session.execute(
            update(WaifuInstance)
            .where(WaifuInstance.id == waifu.id)
            .values(
                xp=new_xp,
                level=new_level,
                last_xp_at=datetime.utcnow(),
            )
        )
        
        # Update user daily XP
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(daily_xp=User.daily_xp + actual_xp)
        )
        
        # Log XP award
        xp_log = XPLog(
            user_id=user_id,
            waifu_id=waifu.id,
            source=source,
            amount=actual_xp,
            meta=meta,
        )
        session.add(xp_log)
        
        await session.commit()
        
        # Check for level up
        level_up = new_level > waifu.level
        return level_up
    
    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """Calculate level from total XP using formula: level = sqrt(xp / 100) + 1"""
        import math
        return int(math.sqrt(xp / 100)) + 1
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """Calculate required XP for a specific level."""
        return 100 * (level - 1) ** 2


# Global XP service instance
xp_service = XPService()

