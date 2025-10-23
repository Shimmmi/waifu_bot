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

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())


