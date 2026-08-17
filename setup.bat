@echo off
echo ===================================
echo DATABASE SETUP
echo ===================================

echo.
echo Step 1: Create database manually in PostgreSQL:
echo   CREATE DATABASE instagram_ai;
echo.
echo Step 2: Run migrations
python manage.py makemigrations
python manage.py migrate

echo.
echo Step 3: Create superuser
python manage.py createsuperuser

echo.
echo Setup complete!
pause
