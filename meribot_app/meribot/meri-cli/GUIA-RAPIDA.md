# meri-cli - Guía Rápida

## Ubicación
Este es el directorio oficial de meri-cli: `/meribot/meri-cli/`

## Instalación

### Opción 1: Uso directo desde el directorio meri-cli
```powershell
cd meribot/meri-cli
.\meri-cli.bat crawl --url "https://example.com" --dominio "example"
```

### Opción 2: Instalación global
```powershell
cd meribot/meri-cli
.\install-meri-cli.ps1 -Install
# Reiniciar terminal
# Desde cualquier directorio:
meri-cli crawl --url "https://example.com" --dominio "example"
```

## Comandos principales

### Crawling básico
```bash
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca"
```

### Crawling con opciones avanzadas
```bash
meri-cli crawl --url "https://cca.capgemini.com/web/home" --dominio "cca" \
  --max-depth 3 \
  --formats "html,pdf" \
  --exclude ".*logout.*" \
  --dry-run
```

### Gestión de base de datos
```bash
meri-cli db --reset
```

## Archivos en este directorio

- `main.py` - Implementación principal del CLI con Click
- `meri-cli.py` - Script ejecutable Python
- `meri-cli.bat` - Script batch para Windows
- `meri-cli.ps1` - Script PowerShell
- `install-meri-cli.ps1` - Instalador para uso global
- `README.md` - Documentación del módulo
- `GUIA-RAPIDA.md` - Esta guía

## Parámetros obligatorios
- `--url`: URL inicial para el crawling
- `--dominio`: Dominio al que pertenece la información

## Requisitos
- Python 3.10+
- Servidor FastAPI ejecutándose en http://localhost:8000 (configurable con --api-host)
- Dominio debe estar en la lista de dominios permitidos en `crawler_config.yaml`

## Estructura de ejecución
```
meri-cli.bat → meri-cli.py → main.py (cli function)
```
