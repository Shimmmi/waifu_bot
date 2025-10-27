from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BotCommand, Message

router = Router()

# Define bot commands for Telegram command menu
BOT_COMMANDS = [
    BotCommand(command="start", description="🚀 Начать игру / Зарегистрироваться"),
    BotCommand(command="profile", description="👤 Профиль пользователя"),
    BotCommand(command="daily", description="🎁 Ежедневный бонус"),
    BotCommand(command="waifu", description="🎭 Управление вайфу"),
    BotCommand(command="stats", description="📊 Статистика"),
]


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Help command showing available commands"""
    help_text = (
        "🤖 <b>Waifu Bot - Список команд</b>\n\n"
        "/start - 🚀 Начать игру и создать профиль\n"
        "/profile - 👤 Посмотреть свой профиль\n"
        "/daily - 🎁 Получить ежедневный бонус\n"
        "/waifu - 🎭 Управление вайфу\n"
        "/stats - 📊 Статистика\n\n"
        "💡 <b>Совет:</b> Используйте кнопки в меню для удобной навигации!"
    )
    await message.answer(help_text, parse_mode="HTML")


async def setup_bot_commands(bot):
    """Set up bot commands in Telegram"""
    await bot.set_my_commands(BOT_COMMANDS)
