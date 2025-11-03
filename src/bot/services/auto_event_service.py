"""
Automatic Event Service

Automatically triggers group events in active groups every hour.
"""
import asyncio
import logging
import random
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from bot.db import SessionLocal
from bot.models import XPLog, User
from bot.data_tables import EVENTS

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


class AutoEventService:
    """Service for automatically triggering group events"""
    
    INTERVAL_SECONDS = 3600  # 1 hour
    
    def __init__(self):
        self.running = False
        self.bot: "Bot | None" = None
    
    async def start(self, bot: "Bot"):
        """Start the automatic event service"""
        self.bot = bot
        self.running = True
        asyncio.create_task(self._event_loop())
        logger.info("✅ Auto event service started")
    
    async def stop(self):
        """Stop the automatic event service"""
        self.running = False
        logger.info("🛑 Auto event service stopped")
    
    async def _event_loop(self):
        """Main loop that triggers events every hour"""
        while self.running:
            try:
                await asyncio.sleep(self.INTERVAL_SECONDS)
                
                if not self.running:
                    break
                
                await self._trigger_events_in_groups()
                
            except Exception as e:
                logger.error(f"Error in auto event loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def _trigger_events_in_groups(self):
        """Trigger events in all active groups"""
        if not self.bot:
            logger.error("Bot not initialized")
            return
        
        session = SessionLocal()
        try:
            # Get all XPLog entries with message source
            result = session.execute(
                select(XPLog.meta)
                .where(XPLog.source == 'message')
                .distinct()
            )
            
            # Extract unique chat_ids from meta JSONB field
            chat_ids = []
            seen_chat_ids = set()
            
            for row in result:
                if row[0] and isinstance(row[0], dict):
                    chat_id = row[0].get('chat_id')
                    if chat_id and chat_id not in seen_chat_ids:
                        try:
                            chat_id_int = int(chat_id)
                            chat_ids.append(chat_id_int)
                            seen_chat_ids.add(chat_id)
                        except (ValueError, TypeError):
                            continue
            
            logger.info(f"Found {len(chat_ids)} active groups for events")
            
            # Trigger event in each group
            for chat_id in chat_ids:
                try:
                    await self._trigger_event_in_group(chat_id)
                except Exception as e:
                    logger.error(f"Error triggering event in chat {chat_id}: {e}", exc_info=True)
            
        except Exception as e:
            logger.error(f"Error getting active groups: {e}", exc_info=True)
        finally:
            session.close()
    
    async def _trigger_event_in_group(self, chat_id: int):
        """Trigger an event in a specific group"""
        if not self.bot:
            return
        
        # Check if there's already an active event
        from bot.services.group_event_system import group_event_manager
        existing_event = group_event_manager.get_event(chat_id)
        
        if existing_event and not existing_event.is_expired():
            logger.info(f"Skipping chat {chat_id}: event already active")
            return
        
        # Select random event type
        event_type = random.choice(list(EVENTS.keys()))
        event = EVENTS[event_type]
        
        # Announce event in group
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"🎪 <b>Начинается соревнование!</b>\n\n"
                    f"🎯 <b>{event['name']}</b>\n"
                    f"📝 {event['description']}\n\n"
                    f"⏱️ У вас есть <b>60 секунд</b> чтобы принять участие!"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to send event announcement to chat {chat_id}: {e}")
            return
        
        # Start the event
        event_state = group_event_manager.start_event(chat_id, event_type)
        
        # Get all users who are members of this chat
        # We need to query XPLog for this
        session = SessionLocal()
        try:
            from bot.models import User
            
            # Get all XPLog entries from this chat
            result = session.execute(
                select(XPLog.user_id, XPLog.meta)
                .where(XPLog.source == 'message')
            )
            
            # Filter and collect unique user_ids from this chat
            user_ids = []
            seen_user_ids = set()
            
            for row in result:
                user_id, meta = row[0], row[1]
                if meta and isinstance(meta, dict):
                    if meta.get('chat_id') == chat_id and user_id not in seen_user_ids:
                        user_ids.append(user_id)
                        seen_user_ids.add(user_id)
            
            # Get users and send invitations
            from bot.services.group_event_system import send_event_invitation, group_event_manager
            
            invitations_sent = 0
            for user_id in user_ids:
                try:
                    # Get user
                    user_result = session.execute(
                        select(User).where(User.id == user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    
                    if not user:
                        continue
                    
                    # Send invitation
                    message_id = await send_event_invitation(
                        self.bot,
                        session,
                        user,
                        event_type,
                        chat_id,
                        event_state.event_id
                    )
                    
                    if message_id:
                        invitations_sent += 1
                        # Add invitation to delete list
                        group_event_manager.add_message_to_delete(chat_id, message_id)
                        
                except Exception as e:
                    logger.error(f"Error sending invitation to user {user_id}: {e}")
                    continue
            
            logger.info(f"Sent {invitations_sent} invitations for event in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error processing event invitations for chat {chat_id}: {e}", exc_info=True)
        finally:
            session.close()
        
        # Schedule finalization after 60 seconds
        async def finalize_after_delay():
            await asyncio.sleep(60)
            from bot.services.group_event_system import finalize_group_event
            
            session = SessionLocal()
            try:
                results_text = await finalize_group_event(self.bot, session, chat_id)
                if results_text:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=results_text,
                        parse_mode="HTML"
                    )
            except Exception as e:
                logger.error(f"Error finalizing event in chat {chat_id}: {e}", exc_info=True)
            finally:
                session.close()
        
        asyncio.create_task(finalize_after_delay())


# Global service instance
auto_event_service = AutoEventService()


async def start_auto_event_service(bot: "Bot"):
    """Start the auto event service"""
    await auto_event_service.start(bot)


async def stop_auto_event_service():
    """Stop the auto event service"""
    await auto_event_service.stop()

