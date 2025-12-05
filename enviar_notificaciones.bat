@echo off
REM Script para enviar notificaciones automaticas
REM Uso: Ejecutar manualmente o desde Task Scheduler

cd /d "%~dp0"

REM Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

REM Ejecutar script de Python con logs
echo ============================================================ >> logs/notificaciones.log
echo Ejecucion: %date% %time% >> logs/notificaciones.log
echo ============================================================ >> logs/notificaciones.log

python scripts/enviar_notificaciones_automaticas.py >> logs/notificaciones.log 2>&1

REM Verificar resultado
if %ERRORLEVEL% EQU 0 (
    echo [OK] Notificaciones enviadas correctamente >> logs/notificaciones.log
) else (
    echo [ERROR] Fallo al enviar notificaciones - Codigo: %ERRORLEVEL% >> logs/notificaciones.log
)

echo. >> logs/notificaciones.log
