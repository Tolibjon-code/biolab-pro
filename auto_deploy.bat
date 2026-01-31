@echo off
echo ========================================
echo 🚀 BioLab Pro Автомат Деплой Скрипти
echo ========================================
echo.

REM 1. Папкага ўтиш
cd "C:\Users\gggfh\Documents\Гормон калибровка 31 январь\biolab-pro"

REM 2. GitHub username сўраш
set /p GITHUB_USER=👉 GitHub username киритинг: 

REM 3. Git командалари
echo ⏳ Git инициализацияси...
git init
git add .
git commit -m "BioLab Pro иловаси"

echo ⏳ GitHub-га уланиш...
git remote add origin https://github.com/%GITHUB_USER%/biolab-pro.git
git branch -M main

echo ⏳ GitHub-га юклаш...
git push -u origin main

echo.
echo ========================================
echo ✅ Код GitHub-га юкланди!
echo 🌐 https://github.com/%GITHUB_USER%/biolab-pro
echo.
echo 🎯 Энди Streamlit Cloud-га ўтинг:
echo 1. https://share.streamlit.io
echo 2. GitHub билан логин
echo 3. New App тугмаси
echo 4. Repository: %GITHUB_USER%/biolab-pro
echo 5. Main file: app.py
echo 6. Deploy!
echo ========================================
pause