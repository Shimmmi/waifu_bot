"""
Automatic stat restoration service for waifus
Restores energy over time
"""
import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

if TYPE_CHECKING:
    from src.bot.models import Waifu

from bot.db import SessionLocal


class StatRestorationService:
    """Service for automatic restoration of waifu stats"""
    
    # Restoration rates (per minute)
    ENERGY_RESTORE_PER_MINUTE = 1  # Restore 1 energy per minute
    MOOD_RESTORE_PER_MINUTE = 0.1  # Restore 0.1 mood per minute
    LOYALTY_RESTORE_PER_MINUTE = 0.05  # Restore 0.05 loyalty per minute
    
    # Maximum values
    MAX_ENERGY = 100
    MAX_MOOD = 100
    MAX_LOYALTY = 100
    
    def __init__(self):
        self.running = False
    
    async def start(self):
        """Start the restoration background task"""
        self.running = True
        asyncio.create_task(self._restoration_loop())
    
    async def stop(self):
        """Stop the restoration background task"""
        self.running = False
    
    async def _restoration_loop(self):
        """Main loop that runs every minute to restore stats"""
        while self.running:
            try:
                await self._restore_all_waifus()
            except Exception as e:
                print(f"Error in stat restoration: {e}")
            
            # Wait 60 seconds before next restoration cycle
            await asyncio.sleep(60)
    
    async def _restore_all_waifus(self):
        """Restore stats for all waifus"""
        session = SessionLocal()
        try:
            from src.bot.models import Waifu
            
            # Get all waifus
            result = session.execute(select(Waifu))
            waifus = result.scalars().all()
            
            now = datetime.now()
            updated_count = 0
            
            for waifu in waifus:
                if self._restore_waifu_stats(waifu, now):
                    updated_count += 1
            
            if updated_count > 0:
                session.commit()
                print(f"✅ Restored stats for {updated_count} waifus")
            
        except Exception as e:
            session.rollback()
            print(f"Error restoring stats: {e}")
        finally:
            session.close()
    
    def _restore_waifu_stats(self, waifu: "Waifu", now: datetime) -> bool:
        """
        Restore stats for a single waifu
        Returns True if waifu was updated
        """
        if not waifu.dynamic:
            # Initialize dynamic stats if not present
            waifu.dynamic = {
                "energy": 100,
                "mood": 50,
                "loyalty": 0,  # Loyalty starts at 0 for new waifus
                "bond": 0,  # Dexterity
                "favor": 0,  # Favor points
                "last_restore": now.isoformat()
            }
            flag_modified(waifu, "dynamic")
            return True
        
        # Get last restore time
        last_restore_str = waifu.dynamic.get("last_restore")
        if not last_restore_str:
            # First time - set last restore to now
            waifu.dynamic["last_restore"] = now.isoformat()
            flag_modified(waifu, "dynamic")
            return True
        
        try:
            last_restore = datetime.fromisoformat(last_restore_str)
        except (ValueError, TypeError):
            # Invalid date format - reset
            waifu.dynamic["last_restore"] = now.isoformat()
            flag_modified(waifu, "dynamic")
            return True
        
        # Calculate minutes since last restore
        time_diff = now - last_restore
        minutes_passed = int(time_diff.total_seconds() / 60)
        
        if minutes_passed < 1:
            # Less than a minute passed, no restoration needed
            return False
        
        # Get current stats
        current_energy = waifu.dynamic.get("energy", 100)
        current_mood = waifu.dynamic.get("mood", 50)
        current_loyalty = waifu.dynamic.get("loyalty", 0)
        
        # Calculate max energy with battery skill
        max_energy = self.MAX_ENERGY
        try:
            from bot.services.skill_effects import get_user_skill_effects
            from bot.models import User
            
            user = session.query(User).filter(User.id == waifu.owner_id).first()
            if user:
                skill_effects = get_user_skill_effects(session, user.id)
                if 'max_energy' in skill_effects:
                    max_energy += int(skill_effects['max_energy'])
        except Exception:
            pass
        
        # Calculate restoration amounts
        energy_to_restore = min(
            minutes_passed * self.ENERGY_RESTORE_PER_MINUTE,
            max_energy - current_energy
        )
        mood_to_restore = min(
            minutes_passed * self.MOOD_RESTORE_PER_MINUTE,
            self.MAX_MOOD - current_mood
        )
        loyalty_to_restore = min(
            minutes_passed * self.LOYALTY_RESTORE_PER_MINUTE,
            self.MAX_LOYALTY - current_loyalty
        )
        
        # Apply skill bonuses to restoration rates
        try:
            from bot.services.skill_effects import get_user_skill_effects
            from bot.models import User
            
            # Get user to fetch skills
            user = session.query(User).filter(User.id == waifu.owner_id).first()
            if user:
                skill_effects = get_user_skill_effects(session, user.id)
                
                # Apply energy recovery bonus
                if 'energy_recovery' in skill_effects:
                    energy_to_restore *= (1.0 + skill_effects['energy_recovery'])
                # Apply mood recovery bonus
                if 'mood_recovery' in skill_effects:
                    mood_to_restore *= (1.0 + skill_effects['mood_recovery'])
                # Apply loyalty growth bonus
                if 'loyalty_growth' in skill_effects:
                    loyalty_to_restore *= (1.0 + skill_effects['loyalty_growth'])
        except Exception:
            # If skill effects fail, just use base rates
            pass
        
        # Apply restoration if needed
        updated = False
        if energy_to_restore > 0 or mood_to_restore > 0 or loyalty_to_restore > 0:
            waifu.dynamic = {
                **waifu.dynamic,
                "energy": int(min(current_energy + energy_to_restore, max_energy)),
                "mood": float(min(current_mood + mood_to_restore, self.MAX_MOOD)),
                "loyalty": int(round(min(current_loyalty + loyalty_to_restore, self.MAX_LOYALTY))),
                "last_restore": now.isoformat()
            }
            flag_modified(waifu, "dynamic")
            updated = True
        
        # Always update last_restore even if nothing was restored
        if not updated:
            waifu.dynamic = {**waifu.dynamic, "last_restore": now.isoformat()}
            flag_modified(waifu, "dynamic")
            updated = True
        
        return updated


# Global instance
_restoration_service: StatRestorationService | None = None


def get_restoration_service() -> StatRestorationService:
    """Get the global stat restoration service instance"""
    global _restoration_service
    if _restoration_service is None:
        _restoration_service = StatRestorationService()
    return _restoration_service


async def start_restoration_service():
    """Start the stat restoration service"""
    service = get_restoration_service()
    await service.start()
    print("✅ Stat restoration service started")


async def stop_restoration_service():
    """Stop the stat restoration service"""
    service = get_restoration_service()
    await service.stop()
    print("🛑 Stat restoration service stopped")

