from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from sqlalchemy import select

from bot.db import SessionLocal
from bot.models import User, Waifu
from bot.services.waifu_generator import format_waifu_card, calculate_waifu_power

router = Router()

@router.message(Command("waifu_card"))
async def cmd_waifu_card(message: Message) -> None:
    """Показать карточку вайфу через web-app (заглушка)"""
    if message.from_user is None:
        return
    
    tg_user_id = message.from_user.id
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await message.answer("Сначала используйте /start")
            return
        
        # Получаем первую вайфу пользователя
        waifu_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id).limit(1)
        )
        waifu = waifu_result.scalar_one_or_none()
        
        if not waifu:
            await message.answer("У вас пока нет вайфу. Используйте призыв!")
            return
        
        # Создаем web-app кнопку (заглушка)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🖼️ Открыть карточку вайфу",
                web_app=WebAppInfo(url="https://example.com/waifu-card")  # Заглушка
            )]
        ])
        
        # Показываем краткую информацию
        power = calculate_waifu_power({
            "stats": waifu.stats,
            "dynamic": waifu.dynamic,
            "level": waifu.level
        })
        
        text = (
            f"🎭 <b>Карточка вайфу</b>\n\n"
            f"👤 {waifu.name}\n"
            f"⭐ Уровень: {waifu.level}\n"
            f"💪 Сила: {power}\n"
            f"🏷️ {waifu.rarity}\n\n"
            f"Нажмите кнопку ниже для просмотра полной карточки:"
        )
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()
