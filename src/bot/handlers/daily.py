from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.db import SessionLocal
from bot.models import User


router = Router()


@router.message(Command("daily"))
async def cmd_daily(message: Message) -> None:
    """Handle daily free pull."""
    if message.from_user is None:
        return
    
    tg_user_id = message.from_user.id
    
    session = SessionLocal()
    try:
        # Get user
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await message.answer("Похоже, ты ещё не зарегистрирован. Нажми /start в ЛС.")
            return
        
        # Simple daily check
        time_left = datetime.utcnow() - user.last_daily.replace(tzinfo=None)
        hours_left = 24 - (time_left.total_seconds() / 3600)
        
        if hours_left > 0:
            await message.answer(
                f"Ежедневный призыв недоступен. "
                f"Осталось ждать: {int(hours_left)} часов."
            )
            return
        
        # Simple daily reward
        user.coins += 50
        user.last_daily = datetime.utcnow()
        session.commit()
        
        await message.answer(
            f"Ежедневный бонус получен! +50 монет\n"
            f"Твой баланс: {user.coins} монет"
        )
        
    except Exception as e:
        await message.answer(f"Ошибка при выполнении призыва: {str(e)}")
    finally:
        session.close()

