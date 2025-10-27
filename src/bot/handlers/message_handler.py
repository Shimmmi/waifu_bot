from aiogram import Router
from aiogram.types import Message
from aiogram.enums import ChatType
import logging

from bot.db import SessionLocal
from bot.models import User
from bot.services.global_xp import global_xp_service

logger = logging.getLogger(__name__)

router = Router()


@router.message()
async def handle_group_message(message: Message) -> None:
    """Handle messages in groups for global XP awarding."""
    if message.from_user is None or message.chat.type == ChatType.PRIVATE:
        return
    
    # Only process messages in groups/supergroups
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
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
        
        # Determine message type and calculate XP
        message_type = "text"
        text_length = 0
        
        if message.text:
            text_length = len(message.text.strip())
            message_type = "text"
        elif message.photo or message.sticker or message.animation:
            message_type = "media"
        elif message.video or message.video_note:
            message_type = "link"  # Video messages
        elif message.voice:
            message_type = "voice"
        elif message.document:
            message_type = "media"  # Treat documents as media
        
        # Check for links in text
        if message.text and message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link", "text_mention"]:
                    message_type = "link"
                    break
        
        # Calculate XP amount
        xp_amount = global_xp_service.calculate_xp_for_message(message_type, text_length)
        
        if xp_amount > 0:
            # Award global XP
            result = await global_xp_service.award_global_xp(
                session=session,
                user_id=user.id,
                xp_amount=xp_amount,
                source="message",
                meta={
                    "message_type": message_type,
                    "text_length": text_length,
                    "chat_id": message.chat.id,
                    "message_id": message.message_id
                }
            )
            
            # Log level up if it occurred
            if result.get("level_up"):
                logger.info(
                    f"🎉 Level up for user {user.username} ({user.id}): "
                    f"Level {result['old_level']} → {result['new_level']} "
                    f"(+{result['skill_points_gained']} skill points)"
                )
        
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
    finally:
        session.close()

