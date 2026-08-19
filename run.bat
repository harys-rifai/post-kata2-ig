@echo off
echo ===================================
echo START DJANGO INSTAGRAM AI
echo ===================================

echo Killing existing processes...
taskkill /F /IM redis-server.exe >nul 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *celery*" /F >nul 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *runserver*" /F >nul 2>nul
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr ":809"') do taskkill /F /PID %%a >nul 2>nul
echo Done killing.

echo Checking Redis...
where redis-server >nul 2>nul
if %errorlevel% == 0 (
    start /b redis-server
    echo Redis started.
    timeout /t 2 >nul
) else (
    if exist "C:\redis\redis-server.exe" (
        start /b "Redis Server" /d C:\redis redis-server.exe redis.windows.conf
        echo Redis started from C:\redis.
        timeout /t 2 >nul
    ) else (
        echo [WARNING] redis-server not found in PATH or C:\redis.
        echo Make sure Redis is running on localhost:6379
        echo Install options:
        echo   - Docker: docker run -d -p 6379:6379 redis
        echo   - Windows: https://github.com/tporadowski/redis/releases
        echo.
    )
)

echo Starting Celery Worker...
start /b celery -A config worker -l info

echo Starting Celery Beat...
start /b celery -A config beat -l info

echo Starting Django on port 809...
python manage.py runserver 809

pause