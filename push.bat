@echo off
echo ===================================
echo PUSH TO GITHUB
echo ===================================
git init
git add .
git commit -m "Initial commit"
git remote remove origin 2>nul
git remote add origin https://github.com/harys-rifai/post-kata2-ig.git
git branch -M main
git push -u origin main
pause
