@echo off
cd /d "%~dp0ecoute"
set "PATH=%PATH%;%USERPROFILE%\tools\ffmpeg\ffmpeg-9.0.1-essentials_build\bin"
REM авто-встановка відсутніх пакетів (швидко, якщо все вже стоїть)
python -m pip install -r requirements.txt -q 2>nul || python -m pip install -r requirements.txt -q --user
python -u main.py --active
if errorlevel 1 (
  echo.
  echo [ERROR] Program exited with an error. See message above.
  pause
)
