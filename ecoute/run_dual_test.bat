@echo off
cd /d "%~dp0ecoute"
set "PATH=%PATH%;%USERPROFILE%\tools\ffmpeg\ffmpeg-9.0.1-essentials_build\bin"
python dual_mic_test.py
pause
