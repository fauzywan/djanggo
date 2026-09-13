@echo off
title Instalasi & Update Dependensi Backend Na Willa
cd /d "%~dp0"

echo =======================================================
echo    Instalasi Dependensi Python (requirements.txt)
echo =======================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Membuat venv...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [INFO] Menjalankan migrasi database...
python manage.py migrate

echo.
echo =======================================================
echo    Selesai! Anda sekarang dapat menjalankan run.bat
echo =======================================================
echo.
pause
