from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery
from sqlalchemy import select
import os

from bot.db import SessionLocal
from bot.models import User


router = Router()

# Get WebApp URL from environment
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://waifu-bot-webapp.onrender.com")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    if message.from_user is None:
        return

    tg_user = message.from_user
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user.id))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                tg_id=tg_user.id,
                username=tg_user.username,
                display_name=tg_user.full_name,
                coins=100,
                gems=0,
            )
            session.add(user)
            session.commit()

        # Создаем кнопки меню
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Профиль", web_app=WebAppInfo(url=f"{WEBAPP_URL}/webapp/profile.html"))],
            [InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data="daily")],
            [InlineKeyboardButton(text="🎭 Вайфу", callback_data="waifu_menu")],
            [InlineKeyboardButton(text="🎯 События", callback_data="events_menu")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton(text="🔧 Debug", callback_data="debug_menu")]
        ])

        await message.answer(
            "Привет! Я Waifu Bot. Твой профиль создан. Выбери действие:",
            reply_markup=keyboard
        )
    finally:
        session.close()



