#!/usr/bin/env python3
"""
Скрипт для запуска API сервера WebApp
"""

import uvicorn
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    # Запуск API сервера
    uvicorn.run(
        "bot.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
