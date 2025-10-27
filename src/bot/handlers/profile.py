from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
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


@router.callback_query(lambda c: c.data == "open_profile")
async def handle_open_profile_callback(callback: CallbackQuery) -> None:
    """Handle profile button callback for groups"""
    if callback.from_user is None:
        return
    
    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await callback.answer("Похоже, ты ещё не зарегистрирован. Нажми /start в ЛС.", show_alert=True)
            return

        text = (
            f"📊 <b>Профиль</b>\n\n"
            f"💰 Монеты: {user.coins}\n"
            f"💎 Гемы: {user.gems}\n"
            f"👤 Уровень: {getattr(user, 'account_level', 1)}\n"
            f"⭐ XP: {getattr(user, 'global_xp', 0)}\n"
            f"🎯 Очки навыков: {getattr(user, 'skill_points', 0)}\n\n"
            f"@{user.username if user.username else '—'}"
        )
        
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()
    finally:
        session.close()


