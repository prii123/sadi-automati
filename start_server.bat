@echo off
echo.
echo ========================================
echo   Iniciando Servidor SADI
echo ========================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m uvicorn api:create_app --factory --host 0.0.0.0 --port 5000 --reload

pause
