#!/usr/bin/env python3
"""
Простой скрипт для запуска бота в фоновом режиме
"""

import subprocess
import sys
import os
from pathlib import Path

def start_bot():
    """Запуск бота в фоновом режиме"""
    try:
        # Проверяем, что мы в правильной директории
        if not Path("run_bot.py").exists():
            print("Ошибка: файл run_bot.py не найден")
            print("Убедитесь, что вы находитесь в корневой директории проекта")
            return
        
        # Запускаем бота в фоновом режиме
        print("Запуск бота в фоновом режиме...")
        process = subprocess.Popen([sys.executable, "run_bot.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print(f"Бот запущен с PID: {process.pid}")
        print("Бот работает в фоновом режиме")
        print("Для остановки бота используйте Ctrl+C или закройте терминал")
        
        # Ждем завершения процесса
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nОстановка бота...")
            process.terminate()
            process.wait()
            print("Бот остановлен")
            
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    start_bot()
