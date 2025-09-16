"""
Endpoint FastAPI para lanzar el procesamiento y chunking de documentos descargados.
Reutiliza la lógica de test_hash_local_docs.py sin modificar ese archivo.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
import os
import yaml
import hashlib
def short_doc_id(rel_path: str, length: int = 10) -> str:
    """Genera un id alfanumérico corto y único a partir de la ruta relativa."""
    return hashlib.sha1(rel_path.encode('utf-8')).hexdigest()[:length]

from meribot.crawler.document_loader import parse_document, chunk_text_with_langchain, process_and_classify_chunks
from meribot.services.storage.chroma_integration import upsert_chunks_to_chroma, get_chroma_collection_and_client, delete_document_by_id
from meribot.services.storage.chroma_integration import list_documents

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
        doc_id = short_doc_id(rel_path)
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

@router.delete("/delete-document")
def delete_document(id: str = Query(..., description="ID del documento a borrar")):
    """
    Elimina un documento y todos sus chunks asociados de la base vectorial (ChromaDB) usando el motor Chroma/LangChain.
    Args:
        id (str): ID del documento a borrar
    Returns:
        dict: Mensaje de éxito o error
    """
    try:
        num_deleted = delete_document_by_id(id)
        return {"status": "success", "message": f"Se eliminaron {num_deleted} chunks asociados al documento '{id}' en ChromaDB."}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar en ChromaDB: {e}")

@router.get("/list-documents")
def list_documents_endpoint(request: Request):
    """
    Endpoint para listar todos los documentos almacenados en la base vectorial (ChromaDB).
    Permite filtrar por cualquier campo usando parámetros de query string.
    Si se pasa show_chunks=true, incluye el número de chunks asociados a cada documento.
    Devuelve una lista de documentos con los campos: ["id", "title", "domain", "date", "chunks"].
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
    Endpoint para obtener el número total de documentos únicos y fragmentos (chunks) almacenados en la base vectorial (ChromaDB).
    Devuelve un diccionario con las claves: total_documents, total_chunks.
    """
    from meribot.services.storage.chroma_integration import count_documents_and_chunks
    try:
        stats = count_documents_and_chunks()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contar documentos y chunks: {e}")
