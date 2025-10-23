from aiogram import Router
from aiogram.types import Message

from bot.db import SessionLocal
from bot.models import User


router = Router()


@router.message()
async def handle_group_message(message: Message) -> None:
    """Handle messages in groups for XP awarding."""
    if message.from_user is None or message.chat.type == "private":
        return
    
    # Only process messages in groups/supergroups
    if message.chat.type not in ["group", "supergroup"]:
        return
    
    tg_user_id = message.from_user.id
    
    session = SessionLocal()
    try:
        # Get user
        from sqlalchemy import select
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            # User not registered, ignore
            return
        
        # Simple XP system - just give coins for messages
        if message.text and len(message.text.strip()) >= 5:
            user.coins += 1
            session.commit()
        
    except Exception:
        # Ignore errors
        pass
    finally:
        session.close()

