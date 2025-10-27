import asyncio
import logging
import sys

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
from bot.handlers.commands import router as commands_router, setup_bot_commands
from bot.services.stat_restoration import start_restoration_service, stop_restoration_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("🚀 Starting Waifu Bot...")
    
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
    dp.include_router(commands_router)
    
    # Set up bot commands in Telegram
    await setup_bot_commands(bot)
    logger.info("✅ Bot commands registered in Telegram")

    # Start stat restoration service
    await start_restoration_service()
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Stop restoration service on shutdown
        await stop_restoration_service()


if __name__ == "__main__":
    asyncio.run(main())


