@echo off
REM Update waifu images to GitHub URLs in production database
REM Replace with your actual Neon database connection string

set DATABASE_URL=postgresql://neondb_owner:npg_REPLACE_WITH_YOUR_PASSWORD@ep-dry-unit-a6kx0mwq.us-west-2.aws.neon.tech/neondb?sslmode=require

python update_waifu_images_github.py

pause

