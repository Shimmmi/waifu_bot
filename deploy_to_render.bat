@echo off
echo.
echo ========================================
echo   DEPLOYING TO RENDER
echo ========================================
echo.

echo Step 1: Adding all changes...
git add .

echo.
echo Step 2: Committing changes...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" (
    git commit -m "Add database logging and fixes"
) else (
    git commit -m "%commit_msg%"
)

echo.
echo Step 3: Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo   DEPLOYMENT INITIATED!
echo ========================================
echo.
echo Render will now automatically deploy your changes.
echo.
echo Next steps:
echo 1. Go to: https://dashboard.render.com
echo 2. Open your Web Service
echo 3. Check "Logs" tab to watch deployment
echo 4. Wait for "Deploy succeeded" message
echo 5. Test your bot in Telegram
echo.
echo Check logs for debug output!
echo See: DEBUGGING_DATABASE_UPDATES.md
echo.
pause

