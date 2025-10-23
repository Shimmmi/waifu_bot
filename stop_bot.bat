@echo off
echo Остановка всех процессов бота...
echo.

REM Завершаем все процессы Python
taskkill /f /im python.exe >nul 2>&1

echo Все процессы бота завершены.
echo Теперь можно запустить бота заново.
echo.
pause
