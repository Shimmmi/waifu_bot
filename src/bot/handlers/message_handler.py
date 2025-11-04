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
    logger.info(f"📨 Received message in chat type: {message.chat.type}")
    
    if message.from_user is None or message.chat.type == ChatType.PRIVATE:
        logger.info("   Skipping: private chat or no user")
        return
    
    # Only process messages in groups/supergroups
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        logger.info(f"   Skipping: wrong chat type ({message.chat.type})")
        return
    
    tg_user_id = message.from_user.id
    logger.info(f"   Processing message from user {tg_user_id} in chat {message.chat.id}")
    
    session = SessionLocal()
    try:
        # Get user
        from sqlalchemy import select
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            logger.info(f"   User {tg_user_id} not found in database - skipping XP award")
            return
        
        logger.info(f"   User found: {user.id} (display_name: {user.display_name})")
        
        # Determine message type and calculate XP
        message_type = "text"
        text_length = 0
        
        if message.text:
            text_length = len(message.text.strip())
            message_type = "text"
            logger.info(f"   Text message: {text_length} chars")
        elif message.photo:
            message_type = "media"
            logger.info("   Photo message")
        elif message.sticker:
            message_type = "media"
            logger.info("   Sticker message")
        elif message.animation:
            message_type = "media"
            logger.info("   Animation message")
        elif message.video or message.video_note:
            message_type = "link"
            logger.info("   Video message")
        elif message.voice:
            message_type = "voice"
            logger.info("   Voice message")
        elif message.document:
            message_type = "media"
            logger.info("   Document message")
        
        # Check for links in text
        if message.text and message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link", "text_mention"]:
                    message_type = "link"
                    logger.info("   Message contains link")
                    break
        
        # Calculate XP and gold amounts
        xp_amount = global_xp_service.calculate_xp_for_message(message_type, text_length)
        gold_amount = global_xp_service.calculate_gold_for_message(message_type, text_length)
        logger.info(f"   Calculated XP: {xp_amount}, Gold: {gold_amount} (type: {message_type})")
        
        if xp_amount > 0 or gold_amount > 0:
            # Award global XP - pass both tg_user_id for rate limiting and user.id for DB
            logger.info(f"   Awarding {xp_amount} XP to user {user.id} (TG: {tg_user_id})")
            # We need to override the rate limit check to use tg_user_id
            # So we'll call the rate limit check separately
            rate_limited = await global_xp_service.is_rate_limited(tg_user_id)
            if rate_limited:
                logger.info(f"   User {tg_user_id} is rate limited")
                return
            
            result = await global_xp_service.award_global_xp(
                session=session,
                user_id=user.id,
                xp_amount=xp_amount,
                gold_amount=gold_amount,
                source="message",
                meta={
                    "message_type": message_type,
                    "text_length": text_length,
                    "chat_id": message.chat.id,
                    "message_id": message.message_id
                },
                skip_rate_limit=True
            )
            
            logger.info(f"   Award result: XP={result.get('global_xp', 0)}, Gold={result.get('gold_awarded', 0)}")
            
            # Log level up if it occurred
            if result.get("level_up"):
                logger.info(
                    f"🎉 Level up for user {user.username} ({user.id}): "
                    f"Level {result['old_level']} → {result['new_level']} "
                    f"(+{result['skill_points_gained']} skill points, "
                    f"+{result.get('gold_awarded', 0)} gold)"
                )
        else:
            logger.info("   No XP awarded (amount = 0)")
        
        # Проверяем активные рейды клана
        if user:
            try:
                from bot.services.clan_raid import ClanRaidService
                raid_service = ClanRaidService()
                raid_result = await raid_service.process_message_for_raid(
                    session=session,
                    user_id=user.id,
                    chat_id=message.chat.id,
                    message=message,
                    bot=message.bot
                )
                if raid_result and raid_result.get('boss_defeated'):
                    logger.info(f"🎉 Boss defeated in raid for user {user.id}!")
            except Exception as e:
                logger.error(f"❌ Error processing raid message: {e}", exc_info=True)
        
    except Exception as e:
        logger.error(f"❌ Error in message handler: {e}", exc_info=True)
    finally:
        session.close()

