# Script de instalación para meri-cli en Windows
# Ejecuta este script desde el directorio meri-cli para configurar meri-cli como comando global

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Help
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MeriCliPath = Join-Path $ScriptDir "meri-cli.bat"

function Show-Help {
    Write-Host "=== Instalador de meri-cli ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Uso (desde el directorio meri-cli):"
    Write-Host "  .\install-meri-cli.ps1 -Install     # Instalar meri-cli como comando global"
    Write-Host "  .\install-meri-cli.ps1 -Uninstall  # Desinstalar meri-cli"
    Write-Host "  .\install-meri-cli.ps1 -Help       # Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Después de la instalación, podrás usar desde cualquier directorio:"
    Write-Host "  meri-cli crawl --url <URL> --dominio <DOMINIO>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ubicación actual del script: $ScriptDir" -ForegroundColor Cyan
}

function Install-MeriCli {
    Write-Host "Instalando meri-cli desde: $ScriptDir" -ForegroundColor Green
    
    # Verificar que el archivo batch existe
    if (-not (Test-Path $MeriCliPath)) {
        Write-Error "No se encontró meri-cli.bat en $MeriCliPath"
        return
    }
    
    # Agregar el directorio meri-cli al PATH del usuario actual
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$ScriptDir*") {
        $newPath = "$currentPath;$ScriptDir"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "Directorio meri-cli agregado al PATH del usuario" -ForegroundColor Green
    } else {
        Write-Host "El directorio meri-cli ya esta en el PATH" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Instalacion completada!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANTE: Reinicia tu terminal o ejecuta:" -ForegroundColor Yellow
    Write-Host "  refreshenv" -ForegroundColor Cyan
    Write-Host "o cierra y abre una nueva terminal para que los cambios surtan efecto." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Después podrás usar desde cualquier directorio:" -ForegroundColor Green
    Write-Host "  meri-cli crawl --url <URL> --dominio <DOMINIO>" -ForegroundColor Cyan
}

function Uninstall-MeriCli {
    Write-Host "Desinstalando meri-cli..." -ForegroundColor Yellow
    
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -like "*$ScriptDir*") {
        $newPath = $currentPath -replace [regex]::Escape(";$ScriptDir"), ""
        $newPath = $newPath -replace [regex]::Escape("$ScriptDir;"), ""
        $newPath = $newPath -replace [regex]::Escape("$ScriptDir"), ""
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "Directorio meri-cli removido del PATH del usuario" -ForegroundColor Green
    } else {
        Write-Host "El directorio meri-cli no estaba en el PATH" -ForegroundColor Yellow
    }
    
    Write-Host "Desinstalacion completada" -ForegroundColor Green
}

# Ejecución principal
if ($Help -or (-not $Install -and -not $Uninstall)) {
    Show-Help
} elseif ($Install) {
    Install-MeriCli
} elseif ($Uninstall) {
    Uninstall-MeriCli
}
