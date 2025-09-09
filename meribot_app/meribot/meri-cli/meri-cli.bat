@echo off
REM Script batch para ejecutar meri-cli desde el directorio meri-cli
REM Uso: meri-cli.bat crawl --url <URL> --dominio <DOMINIO>

REM Obtener la ruta del directorio donde está este archivo
set SCRIPT_DIR=%~dp0

REM Ejecutar el script Python desde el directorio meri-cli
python "%SCRIPT_DIR%meri-cli.py" %*
