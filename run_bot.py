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
    import logging
    from aiohttp import web
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
    from bot.services.stat_restoration import start_restoration_service, stop_restoration_service
    from bot.services.auto_event_service import start_auto_event_service, stop_auto_event_service

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    # Health check endpoint for Render
    async def health_check(request):
        return web.Response(text="Bot is running", status=200)

    async def start_web_server():
        """Start FastAPI server for WebApp and API"""
        import uvicorn
        from bot.api_server import app as fastapi_app
        
        port = int(os.getenv('PORT', 10000))
        
        config = uvicorn.Config(
            fastapi_app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        
        logger.info(f"✅ Starting FastAPI server on port {port}")
        logger.info(f"   WebApp will be available at: http://0.0.0.0:{port}/")
        logger.info(f"   API endpoints at: http://0.0.0.0:{port}/api/waifu/{{id}}")
        
        # Run server in background task
        asyncio.create_task(server.serve())
        return server

    async def main() -> None:
        logger.info("🚀 Starting Waifu Bot...")
        
        # Start FastAPI server first (for Render + WebApp)
        web_server = await start_web_server()
        
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

        logger.info("✅ All routers included")
        
        # Start stat restoration service
        logger.info("🔄 Starting stat restoration service...")
        await start_restoration_service()
        
        # Start auto event service
        logger.info("🔄 Starting auto event service...")
        await start_auto_event_service(bot)
        
        logger.info("✅ Waifu Bot is ready!")
        logger.info("📡 Polling for updates...")
        
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        finally:
            logger.info("🛑 Shutting down...")
            await stop_restoration_service()
            await stop_auto_event_service()

    asyncio.run(main())