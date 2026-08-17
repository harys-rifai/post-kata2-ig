@echo off
cd /d C:\redis

echo ==========================
echo Restarting Redis...
echo ==========================

echo Stopping Redis gracefully...
redis-cli.exe -a Password09! shutdown >nul 2>&1

timeout /t 2 >nul

echo Checking if Redis is still running...
tasklist | findstr /i "redis-server.exe" >nul

if %errorlevel%==0 (
    echo Redis still running. Force killing...
    taskkill /F /IM redis-server.exe >nul 2>&1
    timeout /t 2 >nul
)

echo Starting Redis...
start "Redis Server" redis-server.exe redis.windows.conf

timeout /t 3 >nul

echo Checking Redis status...
redis-cli.exe -a Password09! ping

echo.
echo Restart completed.
pause