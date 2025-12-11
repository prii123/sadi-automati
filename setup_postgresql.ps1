# Script PowerShell para facilitar la migración a PostgreSQL
# Ejecutar con: .\setup_postgresql.ps1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MIGRACIÓN A POSTGRESQL - ASISTENTE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar si Python está instalado
Write-Host "Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python no encontrado. Por favor instala Python 3.8+" -ForegroundColor Red
    exit 1
}

# Verificar si PostgreSQL está instalado
Write-Host "`nVerificando PostgreSQL..." -ForegroundColor Yellow
$pgVersion = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PostgreSQL encontrado: $pgVersion" -ForegroundColor Green
} else {
    Write-Host "⚠ PostgreSQL no encontrado en PATH" -ForegroundColor Yellow
    Write-Host "  Si ya lo instalaste, asegúrate de agregar PostgreSQL al PATH" -ForegroundColor Yellow
    Write-Host "  O continúa y proporciona la información manualmente`n" -ForegroundColor Yellow
}

# Menú de opciones
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ¿QUÉ DESEAS HACER?" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "1. Ejecutar asistente completo (recomendado)" -ForegroundColor White
Write-Host "2. Solo verificar conexión a PostgreSQL" -ForegroundColor White
Write-Host "3. Solo migrar datos desde SQLite" -ForegroundColor White
Write-Host "4. Solo instalar dependencias" -ForegroundColor White
Write-Host "5. Iniciar aplicación" -ForegroundColor White
Write-Host "0. Salir`n" -ForegroundColor White

$opcion = Read-Host "Selecciona una opción (0-5)"

switch ($opcion) {
    "1" {
        Write-Host "`nEjecutando asistente completo..." -ForegroundColor Green
        python scripts/asistente_migracion.py
    }
    "2" {
        Write-Host "`nVerificando conexión a PostgreSQL..." -ForegroundColor Green
        python scripts/verificar_postgresql.py
    }
    "3" {
        Write-Host "`nMigrando datos desde SQLite..." -ForegroundColor Green
        python scripts/migrar_sqlite_a_postgresql.py
    }
    "4" {
        Write-Host "`nInstalando dependencias..." -ForegroundColor Green
        pip install -r requirements.txt
    }
    "5" {
        Write-Host "`nIniciando aplicación..." -ForegroundColor Green
        python servidor.py
    }
    "0" {
        Write-Host "`nSaliendo..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "`n✗ Opción inválida" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PROCESO COMPLETADO" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
