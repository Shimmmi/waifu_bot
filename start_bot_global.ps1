# Start Waifu Bot without virtual environment
# Run: .\start_bot_global.ps1

Write-Host "Starting Waifu Bot (global Python)..."
Write-Host ""

# Set environment variables
$env:BOT_TOKEN="7401283035:AAGiaoJnrzqkuLQYYjNSTPLCReQVdH5oDe4"
$env:DATABASE_URL="sqlite:///./waifu_bot.db"
$env:REDIS_URL="redis://localhost:6379"
$env:ENV="development"

# Start bot
Write-Host "Starting bot..."
Write-Host "Press Ctrl+C to stop"
Write-Host "=================================================="

C:\Users\KhazarzhanTV.SPROJECT\AppData\Local\Programs\Python\Python313\python.exe run_bot.py

Write-Host ""
Write-Host "Bot stopped."
Read-Host "Press Enter to exit"
