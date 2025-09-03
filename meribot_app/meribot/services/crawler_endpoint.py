"""
Endpoint FastAPI para lanzar solo el scraping de documentos.
Reutiliza la lógica de test_hash_local_docs.py para validación y ejecución del scraping.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import yaml
import subprocess

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str
    domain: str

@router.post("/scrape")
def scrape_documents(request: ScrapeRequest):
    url = request.url.strip()
    domain = request.domain.strip()
    if not url:
        raise HTTPException(status_code=400, detail="El parámetro url es obligatorio.")
    if not domain:
        raise HTTPException(status_code=400, detail="El parámetro domain es obligatorio.")

    # Leer allowed_domains desde crawler_config.yaml
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crawler_config.yaml'))
    if not os.path.exists(config_path):
        raise HTTPException(status_code=500, detail=f"No se encontró el archivo de configuración: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    allowed_domains = set(config.get('allowed_domains', []))
    if domain not in allowed_domains:
        raise HTTPException(status_code=400, detail=f"domain no válido: {domain}. Allowed: {allowed_domains}")

    # Directorio de documentos
    DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/scraped/cca.capgemini.com'))
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)

    # Ejecutar scraping
    result = subprocess.run([
        "python", "-m", "meribot.meri-cli.main", "scrape",
        "--url", url,
        "--output", DOCS_DIR
    ], cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')), capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Error en scraping: {result.stderr}")
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_dir": DOCS_DIR
    }
