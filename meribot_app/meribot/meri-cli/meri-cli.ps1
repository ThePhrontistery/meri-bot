# Script PowerShell para ejecutar meri-cli desde el directorio meri-cli
# Uso: .\meri-cli.ps1 crawl --url "https://example.com" --dominio "example"

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Obtener la ruta del directorio donde está este script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Ejecutar el script Python con todos los argumentos
& python "$ScriptDir\meri-cli.py" @Arguments
