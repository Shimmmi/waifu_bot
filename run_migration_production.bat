@echo off
REM Migration script to update production database with waifu images
REM Replace the DATABASE_URL below with your actual Neon connection string

SET DATABASE_URL=postgresql://neondb_owner:npg_L0OgYKFi6dhs@ep-hidden-waterfall-ag469ohh-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require

echo.
echo ========================================
echo Running migration on PRODUCTION database
echo ========================================
echo.

python add_images_to_waifus.py --force

echo.
echo ========================================
echo Migration complete!
echo ========================================
echo.

pause

