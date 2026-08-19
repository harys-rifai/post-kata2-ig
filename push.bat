@echo off
echo ===================================
echo PUSH TO GITHUB
echo ===================================
git add .
git commit -m "Update post-ig"
git push origin main
pause
