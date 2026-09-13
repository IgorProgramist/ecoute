@echo off
cd /d "%~dp0ecoute"
set "PATH=%PATH%;%USERPROFILE%\tools\ffmpeg\ffmpeg-9.0.1-essentials_build\bin"
python main.py
if errorlevel 1 (
  echo.
  echo [ERROR] Program exited with an error. See message above.
  pause
)
