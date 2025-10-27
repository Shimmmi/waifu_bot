"""
Group Event System

Manages group event lifecycle: invitations, participation, and results.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import Session

from bot.models import User, Waifu
from bot.data_tables import EVENTS

logger = logging.getLogger(__name__)


@dataclass
class GroupEventState:
    """State of an active group event"""
    event_id: str
    event_type: str
    chat_id: int
    started_at: datetime
    expires_at: datetime
    participants: Dict[int, str]  # {user_id: waifu_id}
    messages_to_delete: List[int]  # Message IDs to delete after expiration
    results_message_id: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if event has expired"""
        return datetime.utcnow() >= self.expires_at
    
    def time_remaining(self) -> int:
        """Get seconds remaining"""
        if self.is_expired():
            return 0
        return int((self.expires_at - datetime.utcnow()).total_seconds())


class GroupEventManager:
    """Manages active group events"""
    
    def __init__(self):
        self.active_events: Dict[int, GroupEventState] = {}  # {chat_id: event_state}
    
    def start_event(self, chat_id: int, event_type: str) -> GroupEventState:
        """Start a new group event"""
        event_id = f"{chat_id}_{int(datetime.utcnow().timestamp())}"
        expires_at = datetime.utcnow() + timedelta(seconds=60)
        
        state = GroupEventState(
            event_id=event_id,
            event_type=event_type,
            chat_id=chat_id,
            started_at=datetime.utcnow(),
            expires_at=expires_at,
            participants={},
            messages_to_delete=[]
        )
        
        self.active_events[chat_id] = state
        logger.info(f"Started group event {event_id} in chat {chat_id}")
        return state
    
    def get_event(self, chat_id: int) -> Optional[GroupEventState]:
        """Get active event for chat"""
        return self.active_events.get(chat_id)
    
    def end_event(self, chat_id: int) -> Optional[GroupEventState]:
        """End an event and remove from active events"""
        return self.active_events.pop(chat_id, None)
    
    def add_participant(self, chat_id: int, user_id: int, waifu_id: str) -> bool:
        """Add participant to event"""
        if chat_id not in self.active_events:
            return False
        self.active_events[chat_id].participants[user_id] = waifu_id
        logger.info(f"Added participant {user_id} with waifu {waifu_id} to event in chat {chat_id}")
        return True
    
    def add_message_to_delete(self, chat_id: int, message_id: int):
        """Add message ID to delete list"""
        if chat_id in self.active_events:
            self.active_events[chat_id].messages_to_delete.append(message_id)
    
    def set_results_message(self, chat_id: int, message_id: int):
        """Set the results message ID"""
        if chat_id in self.active_events:
            self.active_events[chat_id].results_message_id = message_id


# Global manager instance
group_event_manager = GroupEventManager()


def get_all_registered_users(session: Session) -> List[User]:
    """Get all users registered in the bot"""
    result = session.execute(select(User))
    return list(result.scalars().all())


async def send_event_invitation(
    bot: Bot,
    session: Session,
    user: User,
    event_type: str,
    chat_id: int,
    event_id: str
) -> Optional[int]:
    """
    Send event invitation to a user in private chat.
    Returns message ID if sent successfully, None otherwise.
    """
    try:
        event = EVENTS.get(event_type, {})
        text = (
            f"🎪 <b>Групповое событие!</b>\n\n"
            f"🎯 <b>{event.get('name', 'Событие')}</b>\n"
            f"📝 {event.get('description', 'Описание отсутствует')}\n\n"
            f"⏱️ У тебя есть <b>60 секунд</b> чтобы принять участие!\n\n"
            f"Хочешь участвовать?"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да!", callback_data=f"group_event_yes_{event_id}"),
                InlineKeyboardButton(text="❌ Нет", callback_data=f"group_event_no_{event_id}")
            ]
        ])
        
        message = await bot.send_message(
            chat_id=user.tg_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"Sent event invitation to user {user.tg_id}")
        return message.message_id
        
    except Exception as e:
        logger.error(f"Failed to send invitation to user {user.tg_id}: {e}")
        return None


async def send_event_invitations(
    bot: Bot,
    session: Session,
    event_type: str,
    chat_id: int,
    event_id: str
) -> Dict[int, int]:
    """
    Send event invitations to all registered users.
    Returns dict of {user_id: message_id}
    """
    users = get_all_registered_users(session)
    results = {}
    
    for user in users:
        try:
            message_id = await send_event_invitation(bot, session, user, event_type, chat_id, event_id)
            if message_id:
                results[user.id] = message_id
                # Add invitation to delete list
                group_event_manager.add_message_to_delete(chat_id, message_id)
        except Exception as e:
            logger.error(f"Error sending invitation to user {user.tg_id}: {e}")
    
    logger.info(f"Sent {len(results)} event invitations")
    return results


async def handle_participant_response(
    session: Session,
    user_id: int,
    event_id: str,
    is_accepting: bool,
    waifu_id: Optional[str] = None
) -> tuple[bool, str]:
    """
    Handle participant response to event invitation.
    Returns (success, message)
    """
    try:
        # Get user
        result = session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return False, "Пользователь не найден"
        
        # Find the event by extracting chat_id from event_id
        # event_id format: "{chat_id}_{timestamp}"
        parts = event_id.split('_')
        if len(parts) < 2:
            return False, "Неверный ID события"
        
        chat_id = int(parts[0])
        event_state = group_event_manager.get_event(chat_id)
        
        if not event_state:
            return False, "Событие уже завершено"
        
        if event_state.is_expired():
            return False, "Время на участие истекло"
        
        if not is_accepting:
            # User declined
            return True, "Ты отказался от участия"
        
        # User accepted - need to select waifu
        if not waifu_id:
            # Need to show waifu selection
            return True, "waifu_selection_needed"
        
        # Add participant with selected waifu
        group_event_manager.add_participant(chat_id, user.id, waifu_id)
        return True, "Ты успешно зарегистрировался на событие!"
        
    except Exception as e:
        logger.error(f"Error handling participant response: {e}")
        return False, "Произошла ошибка"


async def finalize_group_event(
    bot: Bot,
    session: Session,
    chat_id: int
) -> Optional[str]:
    """
    Finalize a group event: calculate results and send them.
    Returns results message text.
    """
    event_state = group_event_manager.get_event(chat_id)
    
    if not event_state:
        return None
    
    if not event_state.is_expired():
        # Event not expired yet
        return None
    
    # Remove from active events
    group_event_manager.end_event(chat_id)
    
    # Delete invitation messages in private chats
    for msg_id in event_state.messages_to_delete:
        try:
            # We need to send delete commands to private chats
            # This is complex, so we'll skip this for now
            pass
        except:
            pass
    
    # Calculate results
    if not event_state.participants:
        return "🎪 <b>Групповое событие завершено!</b>\n\n❌ Никто не принял участие."
    
    results = []
    for user_id, waifu_id in event_state.participants.items():
        # Get user
        result = session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            continue
        
        # Get waifu
        waifu_result = session.execute(select(Waifu).where(Waifu.id == waifu_id))
        waifu = waifu_result.scalar_one_or_none()
        
        if not waifu:
            continue
        
        # Calculate score
        from bot.services.event_system import calculate_event_score, get_event_rewards
        score, event_name = calculate_event_score({
            "stats": waifu.stats,
            "profession": waifu.profession,
            "dynamic": waifu.dynamic
        }, event_state.event_type)
        
        rewards = get_event_rewards(score, event_state.event_type)
        
        # Apply rewards
        waifu.xp += rewards["xp"]
        waifu.dynamic["energy"] = max(0, waifu.dynamic["energy"] - 20)
        waifu.dynamic["mood"] = min(100, waifu.dynamic["mood"] + 5)
        waifu.dynamic["loyalty"] = min(100, waifu.dynamic["loyalty"] + 2)
        user.coins += rewards["coins"]
        
        results.append({
            "username": user.username or "User",
            "waifu_name": waifu.name,
            "score": score,
            "rewards": rewards
        })
    
    session.commit()
    
    # Format results
    event = EVENTS.get(event_state.event_type, {})
    text = f"🎪 <b>Групповое событие завершено!</b>\n\n"
    text += f"🎯 <b>{event.get('name', 'Событие')}</b>\n\n"
    
    # Sort by score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    for i, result in enumerate(results[:10], 1):  # Show top 10
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} @{result['username']} ({result['waifu_name']}) - {result['score']} очков\n"
    
    if len(results) > 10:
        text += f"\n... и еще {len(results) - 10} участников"
    
    return text
