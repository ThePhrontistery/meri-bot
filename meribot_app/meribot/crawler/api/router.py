"""
Router FastAPI para todos los endpoints del módulo crawler.
Consolida la funcionalidad de scraping, procesamiento de documentos y gestión de ChromaDB.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
import os
import yaml
import subprocess
import hashlib
import shutil
import re
from typing import Optional

# Importar funciones del crawler
from ..document_loader import parse_document, chunk_text_with_langchain, process_and_classify_chunks
from ..storage.chroma_integration import (
    upsert_chunks_to_chroma, 
    delete_document_by_id, 
    delete_document_by_url, 
    delete_document_by_source_path,
    list_documents, 
    count_documents_and_chunks, 
    get_document_with_chunks
)

# Crear router principal
router = APIRouter(prefix="/crawler", tags=["crawler"])

# ==================== MODELOS PYDANTIC ====================

class Credentials(BaseModel):
    """Modelo para credenciales de autenticación."""
    username: str
    password: str

class ScrapeRequest(BaseModel):
    """Modelo para requests de scraping básico."""
    url: str
    domain: str

class CrawlerRequest(BaseModel):
    """Modelo para requests de crawling completo."""
    url: str
    domain: str
    credentials: Optional[Credentials] = None

class ProcessDocsRequest(BaseModel):
    """Modelo para requests de procesamiento de documentos."""
    url: str
    domain: str

class LoadLocalDocsRequest(BaseModel):
    """Modelo para requests de carga de documentos locales."""
    input_path: str
    domain: str

# ==================== UTILIDADES ====================

def short_doc_id(rel_path: str, length: int = 10) -> str:
    """Genera un id alfanumérico corto y único a partir de la ruta relativa."""
    return hashlib.sha1(rel_path.encode('utf-8')).hexdigest()[:length]

def get_crawler_config():
    """Obtiene la configuración del crawler desde el archivo YAML."""
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../crawler_config.yaml'))
    if not os.path.exists(config_path):
        raise HTTPException(status_code=500, detail=f"No se encontró el archivo de configuración: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate_domain(domain: str) -> bool:
    """Valida que el dominio esté en la lista de dominios permitidos."""
    config = get_crawler_config()
    allowed_domains = set(config.get('allowed_domains', []))
    return domain in allowed_domains

def get_docs_directory():
    """Obtiene el directorio base para documentos scraped."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/scraped'))

def clean_docs_directory(docs_dir: str):
    """Limpia completamente el directorio de documentos."""
    if os.path.exists(docs_dir):
        for root, dirs, files in os.walk(docs_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                shutil.rmtree(os.path.join(root, name))
    else:
        os.makedirs(docs_dir, exist_ok=True)

def find_supported_files(docs_dir: str):
    """Encuentra archivos soportados en el directorio de documentos."""
    EXTS = {'.pdf', '.html', '.htm', '.docx', '.xlsx'}
    archivos_encontrados = []
    
    print(f"[DEBUG] Buscando archivos soportados en: {docs_dir}")
    for root, dirs, files in os.walk(docs_dir):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            fpath = os.path.join(root, fname)
            print(f"[DEBUG] Encontrado archivo: {fpath}")
            
            if ext in EXTS:
                print(f"[DEBUG] Detectado archivo soportado: {fpath}")
                archivos_encontrados.append(fpath)
            elif ext == '':
                # Detectar HTML sin extensión por contenido
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        start = f.read(2048).lower()
                        if start.lstrip().startswith('<!doctype html') or start.lstrip().startswith('<html'):
                            print(f"[DEBUG] Detectado archivo HTML sin extensión: {fpath}")
                            archivos_encontrados.append(fpath)
                except Exception as e:
                    print(f"[ERROR] No se pudo leer el archivo sin extensión {fpath}: {e}")
                    continue
    
    return archivos_encontrados

def execute_scraping(url: str, docs_dir: str, credentials: Optional[Credentials] = None):
    """Ejecuta el scraping usando el nuevo sistema SPAWebScraper."""
    # Importar el sistema de scraping mejorado
    from ..config import load_yaml_config, validate_config
    from ..scraper import create_scraper
    from meribot.utils.logging import get_logger
    
    try:
        # Cargar configuración
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../crawler_config.yaml'))
        config = load_yaml_config(config_path)
        validate_config(config)
        
        # Configurar para la URL específica
        config["seeds"] = [url]
        config["output_dir"] = docs_dir
        config["max_depth"] = 4  # Solo la página inicial para este endpoint
        
        # Extraer dominio de la URL para los dominios permitidos
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Asegurar que el dominio esté permitido
        if domain not in config.get("allowed_domains", []):
            config["allowed_domains"] = config.get("allowed_domains", []) + [domain]
        
        # Crear logger
        logger = get_logger("APIScrapingService")
        
        # Agregar credenciales a la configuración si se proporcionan
        if credentials:
            # Habilitar autenticación en la configuración
            if 'auto_login' not in config:
                config['auto_login'] = {}
            config['auto_login']['enabled'] = True
            config['auto_login']['username'] = credentials.username
            config['auto_login']['password'] = credentials.password
            # Establecer login_url igual a la URL del crawl
            config['auto_login']['login_url'] = url
            logger.info(f"Autenticación habilitada para usuario: {credentials.username}")
            logger.info(f"URL de login establecida igual a URL del crawl: {url}")
        
        # Crear scraper usando factory function (automáticamente usa SPA si está disponible)
        scraper = create_scraper(config, logger=logger)
        
        logger.info(f"Iniciando scraping con {type(scraper).__name__} para: {url}")
        
        # Ejecutar crawling
        scraper.crawl_url(url, depth=4)
        
        # Cerrar recursos si es necesario
        if hasattr(scraper, '_close_selenium_driver'):
            scraper._close_selenium_driver()
        
        logger.info(f"Scraping completado exitosamente. URLs visitadas: {len(scraper.visited)}")
        
        # Simular el objeto result para compatibilidad
        class MockResult:
            def __init__(self):
                self.returncode = 0
                self.stdout = f"Scraping completado con {type(scraper).__name__}. URLs procesadas: {len(scraper.visited)}"
                self.stderr = ""
        
        return MockResult()
        
    except Exception as e:
        logger = get_logger("APIScrapingService")
        logger.error(f"Error en scraping mejorado: {e}")
        raise HTTPException(status_code=500, detail=f"Error en scraping mejorado: {e}")

def get_url_from_file(fpath: str):
    """Obtiene la URL de origen desde el archivo .url asociado."""
    url_path = fpath + ".url"
    url_origen = None
    base_name = os.path.splitext(os.path.basename(fpath))[0]
    base_name_norm = re.sub(r'\\W+', '', base_name).lower()
    
    if os.path.exists(url_path):
        with open(url_path, "r", encoding="utf-8") as f_url:
            url_origen = f_url.read().strip()
            if url_origen:
                url_origen = url_origen.strip()
        print(f"[DEBUG] Archivo .url encontrado para {fpath}: {url_origen}")
    else:
        # Buscar archivo .url alternativo en el mismo directorio
        dir_path = os.path.dirname(fpath)
        for fname in os.listdir(dir_path):
            if fname.endswith('.url'):
                fname_base = os.path.splitext(fname)[0]
                fname_base_norm = re.sub(r'\\W+', '', fname_base).lower()
                if fname_base_norm == base_name_norm:
                    url_file_path = os.path.join(dir_path, fname)
                    try:
                        with open(url_file_path, "r", encoding="utf-8") as f_url:
                            url_origen = f_url.read().strip()
                            if url_origen:
                                url_origen = url_origen.strip()
                            print(f"[DEBUG] Archivo .url alternativo encontrado para {fpath}: {url_origen}")
                            break
                    except Exception:
                        continue
    
    return url_origen

def filter_metadata_for_chroma(metadata: dict) -> dict:
    """Convierte valores complejos en los metadatos a string para compatibilidad con ChromaDB."""
    def convert_value(val):
        if isinstance(val, (list, dict)):
            return str(val)
        return val
    return {k: convert_value(v) for k, v in metadata.items()}

def process_single_document(fpath: str, docs_dir: str, domain: str):
    """Procesa un documento individual y devuelve el resultado."""
    print(f"[DEBUG] process_single_document fpath: {fpath}")
    print(f"[DEBUG] process_single_document docs_dir: {docs_dir}")
    rel_path = os.path.relpath(fpath, docs_dir)
    print(f"[DEBUG] process_single_document rel_path: {rel_path}")
    doc_id = short_doc_id(rel_path)
    
    # Obtener URL de origen
    url_origen = get_url_from_file(fpath)
    print(f"[DEBUG] process_single_document url_origen: {url_origen}")
    
    try:
        doc = parse_document(fpath, url=url_origen or rel_path)
        print(f"[DEBUG] process_single_document doc: {doc}")
    except Exception as e:
        return {"file": rel_path, "error": f"Extracción fallida: {e}"}
    
    print(f"[DEBUG] process_single_document doc.get('error'): {doc.get('error')}")
    print(f"[DEBUG] process_single_document doc.get('text'): {doc.get('text')}")

    if doc.get('error') or not doc.get('text'):
        return {"file": rel_path, "error": doc.get('error', 'Sin texto extraído')}
    
    text = doc['text']
    
    # Forzar almacenamiento de HTML aunque el texto sea mínimo
    ext = os.path.splitext(fpath)[1].lower()
    if not text.strip() or len(text.strip()) < 20:
        if ext in ['.html', '.htm']:
            result = {"file": rel_path, "warning": "HTML: Texto extraído vacío o demasiado corto, pero se almacena igualmente"}
            # Continúa el flujo para HTML
        else:
            return {"file": rel_path, "warning": "Texto extraído vacío o demasiado corto"}
    
    metadata = doc.get('metadata', {})
    metadata['id'] = doc_id
    metadata['source_path'] = rel_path
    metadata['domain'] = domain
    metadata['url'] = url_origen or metadata.get('url')
    # Filtrar metadatos para ChromaDB
    metadata = filter_metadata_for_chroma(metadata)
    
    try:
        chunks = chunk_text_with_langchain(text, chunk_size=800, chunk_overlap=50)
    except Exception as e:
        return {"file": rel_path, "error": f"Chunking fallido: {e}"}
    
    metadata_list = [{**metadata, "chunk_idx": i} for i in range(len(chunks))]
    
    try:
        process_and_classify_chunks(chunks, metadata_list)
    except Exception as e:
        return {"file": rel_path, "error": f"Clasificación fallida: {e}"}
    
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    
    try:
        success = upsert_chunks_to_chroma(chunks, [], metadata_list, ids, persist_dir="chroma_data")
    except Exception as e:
        return {"file": rel_path, "error": f"Almacenamiento fallido: {e}"}
    
    if success:
        return {"file": rel_path, "status": "Chunks almacenados exitosamente"}
    else:
        return {"file": rel_path, "error": "Falló el almacenamiento en ChromaDB"}

# ==================== ENDPOINTS DE SCRAPING ====================

@router.post("/scrape")
def scrape_documents(request: ScrapeRequest):
    """
    Endpoint para ejecutar solo el scraping de documentos.
    Descarga documentos de la URL especificada sin procesarlos.
    """
    url = request.url.strip()
    domain = request.domain.strip()
    
    if not url:
        raise HTTPException(status_code=400, detail="El parámetro url es obligatorio.")
    if not domain:
        raise HTTPException(status_code=400, detail="El parámetro domain es obligatorio.")
    
    if not validate_domain(domain):
        config = get_crawler_config()
        allowed_domains = config.get('allowed_domains', [])
        raise HTTPException(status_code=400, detail=f"domain no válido: {domain}. Allowed: {allowed_domains}")
    
    # Preparar directorio de documentos
    docs_dir = get_docs_directory()
    clean_docs_directory(docs_dir)
    
    # Ejecutar scraping
    result = execute_scraping(url, docs_dir)
    
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_dir": docs_dir
    }

@router.post("/crawl-and-process")
def crawl_and_process(request: CrawlerRequest):
    """
    Endpoint para el proceso completo: crawling, procesamiento, chunking e ingesta.
    Descarga documentos, los procesa y los almacena en ChromaDB.
    """
    url = request.url.strip()
    domain = request.domain.strip()
    
    if not url:
        raise HTTPException(status_code=400, detail="El parámetro url es obligatorio.")
    if not domain:
        raise HTTPException(status_code=400, detail="El parámetro domain es obligatorio.")
    
    if not validate_domain(domain):
        config = get_crawler_config()
        allowed_domains = config.get('allowed_domains', [])
        raise HTTPException(status_code=400, detail=f"domain no válido: {domain}. Allowed: {allowed_domains}")
    
    # Preparar directorio de documentos
    docs_dir = get_docs_directory()
    clean_docs_directory(docs_dir)
    
    # Buscar archivos existentes
    archivos_encontrados = find_supported_files(docs_dir)
    
    if not archivos_encontrados:
        # Ejecutar scraping si no hay archivos
        execute_scraping(url, docs_dir, request.credentials)
        
        print("[DEBUG] Archivos presentes en DOCS_DIR tras scraping:")
        for root, dirs, files in os.walk(docs_dir):
            for fname in files:
                print(os.path.join(root, fname))
        
        archivos_encontrados = find_supported_files(docs_dir)
        
        if not archivos_encontrados:
            raise HTTPException(status_code=404, detail=f"No se encontraron archivos soportados tras el scraping.")
    
    # Procesar cada archivo encontrado
    resultados = []
    for fpath in archivos_encontrados:
        resultado = process_single_document(fpath, docs_dir, domain)
        resultados.append(resultado)
    
    return {"resultados": resultados}

@router.post("/process-docs")
def process_docs(request: ProcessDocsRequest):
    """
    Endpoint para procesar documentos ya descargados.
    Procesa documentos existentes en el directorio sin hacer scraping.
    """
    url = request.url.strip()
    domain = request.domain.strip()
    
    if not url:
        raise HTTPException(status_code=400, detail="El parámetro url es obligatorio.")
    if not domain:
        raise HTTPException(status_code=400, detail="El parámetro domain es obligatorio.")
    
    if not validate_domain(domain):
        config = get_crawler_config()
        allowed_domains = config.get('allowed_domains', [])
        raise HTTPException(status_code=400, detail=f"domain no válido: {domain}. Allowed: {allowed_domains}")
    
    docs_dir = get_docs_directory()
    archivos_encontrados = find_supported_files(docs_dir)
    
    if not archivos_encontrados:
        EXTS = {'.pdf', '.html', '.htm', '.docx', '.xlsx'}
        raise HTTPException(status_code=404, detail=f"No se encontraron archivos soportados ({EXTS}) en {docs_dir}.")
    
    # Procesar cada archivo encontrado
    resultados = []
    for fpath in archivos_encontrados:
        resultado = process_single_document(fpath, docs_dir, domain)
        resultados.append(resultado)
    
    return {"resultados": resultados}

@router.post("/load-local-docs")
def load_local_docs(request: LoadLocalDocsRequest):
    """
    Endpoint para cargar y procesar documentos desde una ruta local personalizada.
    Procesa todos los documentos soportados en la carpeta indicada por input_path, o el archivo indicado si es un archivo.
    """
    input_path = request.input_path.strip()
    domain = request.domain.strip()

    if not input_path:
        raise HTTPException(status_code=400, detail="El parámetro input_path es obligatorio.")
    if not domain:
        raise HTTPException(status_code=400, detail="El parámetro domain es obligatorio.")
    if not os.path.exists(input_path) or (not os.path.isdir(input_path) and not os.path.isfile(input_path)):
        raise HTTPException(status_code=400, detail=f"La ruta indicada no existe o no es un archivo/directorio: {input_path}")
    if not validate_domain(domain):
        config = get_crawler_config()
        allowed_domains = config.get('allowed_domains', [])
        raise HTTPException(status_code=400, detail=f"domain no válido: {domain}. Allowed: {allowed_domains}")

    resultados = []
    if os.path.isdir(input_path):
        archivos_encontrados = find_supported_files(input_path)
        if not archivos_encontrados:
            EXTS = {'.pdf', '.html', '.htm', '.docx', '.xlsx'}
            raise HTTPException(status_code=404, detail=f"No se encontraron archivos soportados ({EXTS}) en {input_path}.")
        for fpath in archivos_encontrados:
            resultado = process_single_document(fpath, input_path, domain)
            resultados.append(resultado)
    elif os.path.isfile(input_path):
        resultado = process_single_document(input_path, os.path.dirname(input_path), domain)
        resultados.append(resultado)

    return {"resultados": resultados}

# ==================== ENDPOINTS DE GESTIÓN DE DOCUMENTOS ====================

@router.delete("/delete-document")
def delete_document(id: str = Query(..., description="ID del documento a borrar")):
    """
    Elimina un documento y todos sus chunks asociados de ChromaDB.
    """
    try:
        num_deleted = delete_document_by_id(id)
        return {
            "status": "success", 
            "message": f"Se eliminaron {num_deleted} chunks asociados al documento '{id}' en ChromaDB."
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar en ChromaDB: {e}")

@router.delete("/delete-document-by-url")
def delete_document_by_url_endpoint(url: str = Query(..., description="URL o ruta fuente del documento a borrar")):
    """
    Elimina todos los chunks asociados a una URL específica en ChromaDB.
    """
    try:
        num_deleted = delete_document_by_url(url)
        return {
            "status": "success", 
            "message": f"Se eliminaron {num_deleted} chunks asociados a la URL '{url}' en ChromaDB."
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar por URL en ChromaDB: {e}")

@router.delete("/delete-document-by-source-path")
def delete_document_by_source_path_endpoint(source_path: str = Query(..., description="source_path del documento a borrar")):
    """
    Elimina todos los chunks asociados a un source_path específico en ChromaDB.
    """
    try:
        num_deleted = delete_document_by_source_path(source_path)
        return {
            "status": "success", 
            "message": f"Se eliminaron {num_deleted} chunks asociados a source_path '{source_path}' en ChromaDB."
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar por source_path en ChromaDB: {e}")

# ==================== ENDPOINTS DE CONSULTA ====================

@router.get("/list-documents")
def list_documents_endpoint(request: Request):
    """
    Lista todos los documentos almacenados en ChromaDB.
    Permite filtrar por cualquier campo usando parámetros de query string.
    """
    try:
        filters = dict(request.query_params)
        show_chunks = filters.pop("show_chunks", "false").lower() == "true"
        docs = list_documents(filters=filters, show_chunks=show_chunks)
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar documentos: {e}")

@router.get("/count-documents")
def count_documents_endpoint():
    """
    Obtiene el número total de documentos únicos y chunks almacenados en ChromaDB.
    """
    try:
        stats = count_documents_and_chunks()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contar documentos y chunks: {e}")

@router.get("/show-document")
def show_document_endpoint(id: str = Query(..., description="ID del documento a mostrar")):
    """
    Muestra los metadatos y fragmentos asociados a un documento por su ID.
    """
    result = get_document_with_chunks(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"No existe un documento con id: {id}")
    return result

@router.get("/health")
def health_check():
    """
    Endpoint de salud para verificar que el servicio del crawler está funcionando.
    """
    return {
        "status": "healthy",
        "service": "meribot-crawler",
        "version": "1.0.0"
    }