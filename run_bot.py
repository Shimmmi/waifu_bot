#!/usr/bin/env python3
"""
Простой скрипт для запуска Waifu Bot
"""
import sys
import os
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Теперь импортируем и запускаем бота
if __name__ == "__main__":
    import asyncio
    from bot.main import main
    
    print("Запуск Waifu Bot...")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        print("Проверьте настройки в файле .env")
