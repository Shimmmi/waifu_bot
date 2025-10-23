from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from bot.db import SessionLocal
from bot.models import User


router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    if message.from_user is None:
        return

    tg_user_id = message.from_user.id
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await message.answer("Похоже, ты ещё не зарегистрирован. Нажми /start в ЛС.")
            return

        text = (
            f"Профиль\n"
            f"Монеты: {user.coins}\n"
            f"Гемы: {user.gems}\n"
            f"Ник: @{user.username if user.username else '—'}\n"
        )
        await message.answer(text)
    finally:
        session.close()



