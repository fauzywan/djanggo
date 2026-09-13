@echo off
title Menjalankan Unit Test Backend Django
cd /d "%~dp0"

echo =======================================================
echo    Menjalankan Test Suite Sentimen Na Willa
echo =======================================================
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python manage.py test sentiment_api

echo.
pause
