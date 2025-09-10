"""
Endpoint FastAPI para lanzar el proceso completo de crawling y procesamiento de documentos.
Reutiliza la lógica de test_hash_local_docs.py sin modificar ese archivo.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import yaml
import subprocess

# Importar funciones necesarias
from meribot.crawler.document_loader import parse_document, chunk_text_with_langchain, process_and_classify_chunks
from meribot.services.storage.chroma_integration import upsert_chunks_to_chroma, query_similar_chunks

router = APIRouter()

class CrawlerRequest(BaseModel):
    url: str
    domain: str

@router.post("/crawl-and-process")
def crawl_and_process(request: CrawlerRequest):
    """
    Lanza el proceso completo: descarga, procesamiento, chunking e ingesta.
    """
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
    EXTS = {'.pdf', '.html', '.htm', '.docx', '.xlsx'}
    # Limpieza de la carpeta antes de ejecutar el flujo completo
    import shutil
    if os.path.exists(DOCS_DIR):
        for root, dirs, files in os.walk(DOCS_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                shutil.rmtree(os.path.join(root, name))
    else:
        os.makedirs(DOCS_DIR, exist_ok=True)

    archivos_encontrados = []
    print("[DEBUG] Buscando archivos soportados en:", DOCS_DIR)
    for root, dirs, files in os.walk(DOCS_DIR):
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

    if not archivos_encontrados:
        # Ejecutar scraping
        result = subprocess.run([
            "python", "-m", "meribot.meri-cli.main", "scrape",
            "--url", url,
            "--output", DOCS_DIR
        ], cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')), capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error en scraping: {result.stderr}")
        print("[DEBUG] Archivos presentes en DOCS_DIR tras scraping:")
        for root, dirs, files in os.walk(DOCS_DIR):
            for fname in files:
                print(os.path.join(root, fname))
        archivos_encontrados = []
        for root, dirs, files in os.walk(DOCS_DIR):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                fpath = os.path.join(root, fname)
                if ext in EXTS:
                    archivos_encontrados.append(fpath)
                elif ext == '':
                    # Detectar HTML sin extensión por contenido (tras scraping)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            start = f.read(2048).lower()
                            if start.lstrip().startswith('<!doctype html') or start.lstrip().startswith('<html'):
                                archivos_encontrados.append(fpath)
                    except Exception as e:
                        print(f"[ERROR] No se pudo leer el archivo sin extensión {fpath}: {e}")
                        continue
        if not archivos_encontrados:
            raise HTTPException(status_code=404, detail=f"No se encontraron archivos soportados ({EXTS}) tras el scraping.")

    resultados = []
    import re
    for fpath in archivos_encontrados:
        rel_path = os.path.relpath(fpath, DOCS_DIR)
        doc_id = rel_path.replace(os.sep, '_')
        # Leer la URL de origen desde el archivo .url si existe
        url_path = fpath + ".url"
        url_origen = None
        base_name = os.path.splitext(os.path.basename(fpath))[0]
        base_name_norm = re.sub(r'\W+', '', base_name).lower()
        if os.path.exists(url_path):
            with open(url_path, "r", encoding="utf-8") as f_url:
                url_origen = f_url.read().strip()
                if url_origen:
                    url_origen = url_origen.strip()
            print(f"[DEBUG] Archivo .url encontrado para {fpath}: {url_origen}")
        else:
            # Refuerzo: buscar cualquier .url en el mismo directorio si el exacto no existe, ignorando mayúsculas/minúsculas y espacios
            dir_path = os.path.dirname(fpath)
            for fname in os.listdir(dir_path):
                if fname.endswith('.url'):
                    fname_base = os.path.splitext(fname)[0]
                    fname_base_norm = re.sub(r'\W+', '', fname_base).lower()
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
        try:
            doc = parse_document(fpath, url=url_origen or rel_path)
        except Exception as e:
            resultados.append({"file": rel_path, "error": f"Extracción fallida: {e}"})
            continue
        if doc.get('error') or not doc.get('text'):
            resultados.append({"file": rel_path, "error": doc.get('error', 'Sin texto extraído')})
            continue
        text = doc['text']
        # Forzar almacenamiento de HTML aunque el texto sea mínimo
        ext = os.path.splitext(fpath)[1].lower()
        if not text.strip() or len(text.strip()) < 20:
            if ext in ['.html', '.htm']:
                resultados.append({"file": rel_path, "warning": "HTML: Texto extraído vacío o demasiado corto, pero se almacena igualmente"})
                # Continúa el flujo para HTML
            else:
                resultados.append({"file": rel_path, "warning": "Texto extraído vacío o demasiado corto"})
                continue
        metadata = doc.get('metadata', {})
        metadata['id'] = doc_id
        metadata['source_path'] = rel_path
        metadata['domain'] = domain
        # Refuerzo: Sobrescribe SIEMPRE el campo url con la URL de origen leída del .url
        metadata['url'] = url_origen or metadata.get('url')
        try:
            chunks = chunk_text_with_langchain(text, chunk_size=800, chunk_overlap=50)
        except Exception as e:
            resultados.append({"file": rel_path, "error": f"Chunking fallido: {e}"})
            continue
        metadata_list = [{**metadata, "chunk_idx": i} for i in range(len(chunks))]
        try:
            process_and_classify_chunks(chunks, metadata_list)
        except Exception as e:
            resultados.append({"file": rel_path, "error": f"Clasificación fallida: {e}"})
            continue
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    # ...existing code...
        try:
            success = upsert_chunks_to_chroma(chunks, [], metadata_list, ids, persist_dir="chroma_data")
        except Exception as e:
            resultados.append({"file": rel_path, "error": f"Almacenamiento fallido: {e}"})
            continue
        if success:
            resultados.append({"file": rel_path, "status": "Chunks almacenados exitosamente"})
        else:
            resultados.append({"file": rel_path, "error": "Falló el almacenamiento en ChromaDB"})
    return {"resultados": resultados}
