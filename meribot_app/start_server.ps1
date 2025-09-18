# Script para iniciar MeriBot con FastAPI + Frontend en puerto 8000
# =================================================================

Write-Host "Iniciando MeriBot Server..." -ForegroundColor Green
Write-Host "FastAPI + Frontend Web en puerto 8000" -ForegroundColor Yellow

# Cambiar al directorio correcto
Set-Location -Path $PSScriptRoot

# Verificar que existe el entorno virtual
$venvPath = "..\\.venv\\Scripts\\python.exe"
if (-not (Test-Path $venvPath)) {
    Write-Host "Error: No se encontro el entorno virtual en ../.venv/" -ForegroundColor Red
    Write-Host "Ejecuta primero: configure_python_environment" -ForegroundColor Yellow
    exit 1
}

# Configurar variables de entorno
$env:PYTHONPATH = $PSScriptRoot
Write-Host "PYTHONPATH configurado: $($env:PYTHONPATH)" -ForegroundColor Cyan

# Verificar que existe el archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "Advertencia: No se encontro archivo .env" -ForegroundColor Yellow
} else {
    Write-Host "Archivo .env encontrado" -ForegroundColor Green
}

# Mostrar información del servidor
Write-Host "" -ForegroundColor White
Write-Host "Servidor iniciando en:" -ForegroundColor White
Write-Host "   API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "   Widget: http://localhost:8000/widget" -ForegroundColor Cyan
Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White

# Iniciar uvicorn
Write-Host "Iniciando uvicorn con recarga automatica..." -ForegroundColor Green
try {
    & $venvPath -m uvicorn meribot.core.api.app:app --reload --host 127.0.0.1 --port 8000
} catch {
    Write-Host "Error al iniciar el servidor: $_" -ForegroundColor Red
    exit 1
}