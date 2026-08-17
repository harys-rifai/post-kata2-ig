@echo off
echo ===================================
echo START DJANGO INSTAGRAM AI
echo ===================================

echo Checking Redis...
where redis-server >nul 2>nul
if %errorlevel% == 0 (
    start /b redis-server
    echo Redis started.
    timeout /t 2 >nul
) else (
    echo [WARNING] redis-server not found in PATH.
    echo Make sure Redis is running on localhost:6379
    echo Install options:
    echo   - WSL: wsl sudo apt install redis-server ^& wsl redis-server
    echo   - Docker: docker run -d -p 6379:6379 redis
    echo   - Windows: https://github.com/tporadowski/redis/releases
    echo.
)

echo Starting Celery Worker...
start /b celery -A config worker -l info

echo Starting Celery Beat...
start /b celery -A config beat -l info

echo Starting Django on port 809...
python manage.py runserver 809

pause
