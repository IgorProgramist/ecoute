@echo off
cd /d "%~dp0ecoute"
set "PY=python"
py -3.14 -c "" >nul 2>nul && set "PY=py -3.14"
REM авто-встановка відсутніх пакетів (швидко, якщо все вже стоїть)
%PY% -m pip install -r requirements.txt -q 2>nul || %PY% -m pip install -r requirements.txt -q --user
%PY% -u main.py --active
if errorlevel 1 (
  echo.
  echo [ERROR] Program exited with an error. See message above.
  pause
)
