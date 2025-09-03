"""
Endpoint FastAPI para lanzar el procesamiento y chunking de documentos descargados.
Reutiliza la lógica de test_hash_local_docs.py sin modificar ese archivo.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import yaml

from meribot.crawler.document_loader import parse_document, chunk_text_with_langchain, process_and_classify_chunks
from meribot.services.storage.chroma_integration import upsert_chunks_to_chroma

router = APIRouter()

class ProcessDocsRequest(BaseModel):
    url: str
    domain: str

@router.post("/process-docs")
def process_docs(request: ProcessDocsRequest):
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

    DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/scraped/cca.capgemini.com'))
    EXTS = {'.pdf', '.html', '.htm', '.docx', '.xlsx'}

    archivos_encontrados = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in EXTS:
                archivos_encontrados.append(os.path.join(root, fname))
    if not archivos_encontrados:
        raise HTTPException(status_code=404, detail=f"No se encontraron archivos soportados ({EXTS}) en {DOCS_DIR}.")

    resultados = []
    for fpath in archivos_encontrados:
        rel_path = os.path.relpath(fpath, DOCS_DIR)
        doc_id = rel_path.replace(os.sep, '_')
        try:
            doc = parse_document(fpath, url=rel_path)
        except Exception as e:
            resultados.append({"file": rel_path, "error": f"Extracción fallida: {e}"})
            continue
        if doc.get('error') or not doc.get('text'):
            resultados.append({"file": rel_path, "error": doc.get('error', 'Sin texto extraído')})
            continue
        text = doc['text']
        if not text.strip() or len(text.strip()) < 20:
            resultados.append({"file": rel_path, "warning": "Texto extraído vacío o demasiado corto"})
            continue
        metadata = doc.get('metadata', {})
        metadata['id'] = doc_id
        metadata['source_path'] = rel_path
        metadata['domain'] = domain
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
