@echo off
title Backend Django Na Willa
cd /d "%~dp0"

echo =======================================================
echo    Menjalankan Server Backend Django Na Willa
echo =======================================================
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python manage.py migrate

echo.
echo Server aktif di: http://127.0.0.1:8000/
echo Tekan CTRL+C untuk mematikan server.
echo.

python manage.py runserver 8000

echo.
pause
