#!/usr/bin/env python3
"""
Скрипт для запуска бота Waifu Bot
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Устанавливаем рабочую директорию
os.chdir(project_root)

if __name__ == "__main__":
    import asyncio
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    from bot.config import get_settings
    from bot.handlers.start import router as start_router
    from bot.handlers.profile import router as profile_router
    from bot.handlers.daily import router as daily_router
    from bot.handlers.message_handler import router as message_router
    from bot.handlers.menu import router as menu_router
    from bot.handlers.waifu import router as waifu_router
    from bot.handlers.debug import router as debug_router
    from bot.handlers.webapp import router as webapp_router

    async def main() -> None:
        settings = get_settings()
        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()

        # Include routers
        dp.include_router(start_router)
        dp.include_router(profile_router)
        dp.include_router(daily_router)
        dp.include_router(message_router)
        dp.include_router(menu_router)
        dp.include_router(waifu_router)
        dp.include_router(debug_router)
        dp.include_router(webapp_router)

        print("Запуск Waifu Bot...")
        print("Бот готов к работе!")
        
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    asyncio.run(main())