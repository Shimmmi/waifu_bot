@echo off
REM Update waifu images to GitHub URLs in production database
REM Replace with your actual Neon database connection string

set DATABASE_URL=psql 'postgresql://neondb_owner:npg_L0OgYKFi6dhs@ep-hidden-waterfall-ag469ohh-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require'

python update_waifu_images_github.py

pause

