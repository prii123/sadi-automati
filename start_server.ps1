# Script para iniciar el servidor de desarrollo
Write-Host "🚀 Iniciando servidor SADI..." -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual y ejecutar uvicorn
& ".\venv\Scripts\python.exe" -m uvicorn api:create_app --factory --host 0.0.0.0 --port 5000 --reload
