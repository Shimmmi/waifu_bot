import random
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, WaifuTemplate, WaifuInstance, PullHistory, Transaction


class GachaService:
    # Rarity rates: Common 85%, Uncommon 10%, Rare 3%, Epic 1.5%, Legendary 0.5%
    RARITY_RATES = {
        "common": 0.85,
        "uncommon": 0.10,
        "rare": 0.03,
        "epic": 0.015,
        "legendary": 0.005,
    }
    
    PITY_THRESHOLD = 50  # Guaranteed Rare after 50 pulls without Rare+
    
    @classmethod
    async def get_available_templates(cls, session: AsyncSession) -> list[WaifuTemplate]:
        """Get all available waifu templates for gacha."""
        result = await session.execute(select(WaifuTemplate))
        return list(result.scalars().all())
    
    @classmethod
    def roll_rarity(cls, pity_counter: int) -> str:
        """Roll rarity based on rates and pity system."""
        # Check pity first
        if pity_counter >= cls.PITY_THRESHOLD:
            return "rare"  # Guaranteed rare or better
        
        # Normal roll
        roll = random.random()
        cumulative = 0.0
        
        for rarity, rate in cls.RARITY_RATES.items():
            cumulative += rate
            if roll <= cumulative:
                return rarity
        
        return "common"  # Fallback
    
    @classmethod
    async def select_template_by_rarity(
        cls, session: AsyncSession, rarity: str
    ) -> WaifuTemplate | None:
        """Select a random template of the specified rarity."""
        result = await session.execute(
            select(WaifuTemplate).where(WaifuTemplate.rarity == rarity)
        )
        templates = list(result.scalars().all())
        return random.choice(templates) if templates else None
    
    @classmethod
    async def perform_pull(
        cls, 
        session: AsyncSession, 
        user_id: int, 
        pull_type: str = "daily"
    ) -> dict[str, Any]:
        """Perform a single gacha pull."""
        # Get user
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Roll rarity
        rarity = cls.roll_rarity(user.pity_counter)
        
        # Select template
        template = await cls.select_template_by_rarity(session, rarity)
        if not template:
            # Fallback to common if rarity not found
            template = await cls.select_template_by_rarity(session, "common")
            if not template:
                raise ValueError("No templates available")
        
        # Create waifu instance
        waifu = WaifuInstance(
            owner_id=user_id,
            template_id=template.template_id,
            level=1,
            xp=0,
            affection=0,
        )
        session.add(waifu)
        await session.flush()  # Get the ID
        
        # Update user pity counter
        new_pity_counter = 0 if rarity in ["rare", "epic", "legendary"] else user.pity_counter + 1
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(pity_counter=new_pity_counter)
        )
        
        # Log pull history
        pull_log = PullHistory(
            user_id=user_id,
            type=pull_type,
            cost={"coins": 0, "gems": 0} if pull_type == "daily" else {"coins": 3000, "gems": 0},
            result={
                "waifu_id": waifu.id,
                "template_code": template.code,
                "rarity": rarity,
                "pity_counter": new_pity_counter,
            },
            pity_counter=new_pity_counter,
        )
        session.add(pull_log)
        
        # Log transaction if paid
        if pull_type != "daily":
            transaction = Transaction(
                user_id=user_id,
                kind="spend",
                amount=3000,
                currency="coins",
                reason=f"gacha_{pull_type}",
                meta={"waifu_id": waifu.id, "rarity": rarity},
            )
            session.add(transaction)
            
            # Deduct coins
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(coins=User.coins - 3000)
            )
        
        await session.commit()
        
        return {
            "waifu_id": waifu.id,
            "template": template,
            "rarity": rarity,
            "pity_counter": new_pity_counter,
            "is_pity": user.pity_counter >= cls.PITY_THRESHOLD,
        }
    
    @classmethod
    async def can_daily_pull(cls, session: AsyncSession, user_id: int) -> bool:
        """Check if user can perform daily pull."""
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return False
        
        # Check if 24 hours have passed since last daily
        time_since_last = datetime.utcnow() - user.last_daily.replace(tzinfo=None)
        return time_since_last >= timedelta(hours=24)
    
    @classmethod
    async def update_daily_streak(cls, session: AsyncSession, user_id: int) -> None:
        """Update user's daily streak and last_daily timestamp."""
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                last_daily=datetime.utcnow(),
                daily_streak=User.daily_streak + 1,
            )
        )

