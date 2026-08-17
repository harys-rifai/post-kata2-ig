@echo off
set /p msg=Commit Message:
git add .
git commit -m "%msg%"
git push origin main
pause
