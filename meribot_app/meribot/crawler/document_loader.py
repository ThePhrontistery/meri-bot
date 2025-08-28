# ================= Ejemplo de integración tras el chunking =================
# Supón que tienes un documento procesado y quieres fragmentarlo y clasificar los chunks:
#
# from meribot.crawler.document_loader import semantic_chunk_text, process_and_classify_chunks
#
# text = "...texto extraído del documento..."
# metadata = {"id": "doc1", "url": "http://ejemplo.com/doc1"}  # Ajusta según tus metadatos
# chunks = semantic_chunk_text(text)
# metadata_list = [{**metadata, "chunk_idx": i} for i in range(len(chunks))]
# resultados = process_and_classify_chunks(chunks, metadata_list)
# for chunk, meta, estado in resultados:
#     print(f"Chunk {meta['chunk_idx']} ({meta.get('id') or meta.get('url')}): {estado}")
# ===========================================================================
from dotenv import load_dotenv
load_dotenv()


import numpy as np
from typing import List, Optional
import requests
import os
import json

# --- Utilidades de hash y persistencia ---
from meribot.utils.hash_utils import calculate_sha256, load_hash_db, save_hash_db

# Ruta por defecto para la base de datos de hashes (puedes cambiarla)
HASH_DB_PATH = os.getenv('HASH_DB_PATH', 'hash_db.json')
# Ejemplo de función para procesar y clasificar chunks según hash
def process_and_classify_chunks(chunks: list, metadata_list: list, hash_db_path: str = HASH_DB_PATH):
    """
    Procesa una lista de chunks y los clasifica como 'nuevo', 'modificado' o 'sin cambios' usando hashes persistentes.
    :param chunks: Lista de textos (chunks)
    :param metadata_list: Lista de metadatos asociados a cada chunk (debe tener un campo 'id' o similar)
    :param hash_db_path: Ruta al archivo JSON de hashes
    :return: Lista de tuplas (chunk, metadata, estado)
    """
    hash_db = load_hash_db(hash_db_path)
    resultados = []
    for chunk, meta in zip(chunks, metadata_list):
        chunk_id = meta.get('id') or meta.get('url') or meta.get('title') or str(hash(chunk))
        chunk_hash = calculate_sha256(chunk)
        prev_hash = hash_db.get(chunk_id)
        if prev_hash is None:
            estado = 'nuevo'
        elif prev_hash == chunk_hash:
            estado = 'sin cambios'
        else:
            estado = 'modificado'
        hash_db[chunk_id] = chunk_hash
        resultados.append((chunk, meta, estado))
    save_hash_db(hash_db, hash_db_path)
    return resultados

def get_azure_openai_embeddings(sentences: list[str]) -> np.ndarray:
    """
    Obtiene embeddings de Azure OpenAI para una lista de frases.
    Requiere las variables de entorno:
        AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")
    deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
    if not endpoint or not api_key or not deployment:
        raise RuntimeError("Faltan variables de entorno para Azure OpenAI embeddings.")
    url = f"{endpoint}/openai/deployments/{deployment}/embeddings?api-version=2023-05-15"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    data = {"input": sentences}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise RuntimeError(f"Error Azure OpenAI: {response.status_code} {response.text}")
    result = response.json()
    # El resultado es una lista de dicts con 'embedding' en el mismo orden
    embeddings = [item["embedding"] for item in result["data"]]
    return np.array(embeddings)

def semantic_chunk_text(
    text: str,
    max_chunk_size: int = 500,
    min_chunk_size: int = 200,
    stride: int = 50,
    split_on_newline: bool = True,
    similarity_threshold: float = 0.7,
    return_embeddings: bool = False
) -> List[str]:
    """
    Divide el texto en fragmentos semánticamente coherentes usando embeddings de Azure OpenAI.
    Obtiene los embeddings vía API y agrupa frases en chunks según similitud.

    Args:
        text (str): Texto a fragmentar.
        max_chunk_size (int): Máximo de caracteres por chunk.
        min_chunk_size (int): Mínimo de caracteres por chunk.
        stride (int): Superposición de caracteres entre chunks.
        split_on_newline (bool): Si True, divide primero por saltos de línea.
        similarity_threshold (float): Umbral de similitud para unir frases.
        return_embeddings (bool): Si True, retorna tuplas (chunk, embedding).

    Returns:
        List[str] o List[Tuple[str, np.ndarray]]: Lista de chunks (y opcionalmente embeddings).
    """

    # --- División en frases ---
    if split_on_newline:
        sentences = [s.strip() for s in text.split("\n") if s.strip()]
    else:
        import re
        sentences = re.split(r'(?<=[.!?]) +', text)
        sentences = [s.strip() for s in sentences if s.strip()]


    # Filtrar frases vacías o muy cortas y limitar a las primeras 50 para pruebas rápidas
    sentences = [s for s in sentences if len(s) > 10][:50]
    print(f"[DEBUG] Frases para embeddings (total: {len(sentences)}):")
    for i, s in enumerate(sentences[:10]):
        print(f"  {i+1}: {s[:80]}{'...' if len(s) > 80 else ''}")
    if len(sentences) > 10:
        print(f"  ... ({len(sentences)-10} frases más)")
    if not sentences:
        print("[ADVERTENCIA] No hay frases válidas para embeddings. Se omite el chunking.")
        return []


    # --- Obtener embeddings desde Azure OpenAI en lotes ---
    MAX_EMBEDDINGS_BATCH = 1000
    embeddings = []
    for i in range(0, len(sentences), MAX_EMBEDDINGS_BATCH):
        batch = sentences[i:i+MAX_EMBEDDINGS_BATCH]
        print(f"[DEBUG] Solicitando embeddings para frases {i+1}-{i+len(batch)}")
        batch_embs = get_azure_openai_embeddings(batch)
        embeddings.extend(batch_embs)

    # --- Chunking semántico configurable ---
    chunks = []
    current_chunk = []
    current_len = 0
    last_emb = None
    for i, (sent, emb) in enumerate(zip(sentences, embeddings)):
        if not current_chunk:
            current_chunk.append(sent)
            current_len = len(sent)
            last_emb = emb
            continue
        # Calcular similitud coseno con el último embedding del chunk usando NumPy
        sim = float(np.dot(emb, last_emb) / (np.linalg.norm(emb) * np.linalg.norm(last_emb)))
        if (current_len + len(sent) <= max_chunk_size and sim >= similarity_threshold) or current_len < min_chunk_size:
            current_chunk.append(sent)
            current_len += len(sent)
            last_emb = emb
        else:
            chunks.append(" ".join(current_chunk))
            # Solapamiento opcional
            if stride > 0 and len(current_chunk) > 1:
                overlap = current_chunk[-stride:] if stride < len(current_chunk) else current_chunk
                current_chunk = list(overlap)
                current_len = sum(len(s) for s in current_chunk)
                last_emb = get_azure_openai_embeddings([current_chunk[-1]])[0]
            else:
                current_chunk = [sent]
                current_len = len(sent)
                last_emb = emb
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    if return_embeddings:
        chunk_embs = get_azure_openai_embeddings(chunks)
        return list(zip(chunks, chunk_embs))
    return chunks
# Fragmentación de texto
def split_text(text: str, max_length: int = 1000) -> list:
    """
    Fragmenta el texto en trozos de longitud máxima, procurando no cortar frases ni palabras.
    """
    if not isinstance(text, str) or max_length <= 0:
        return [text]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ''
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_length:
            current += (' ' if current else '') + sentence
        else:
            if current:
                chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())
    return chunks
# Normalización de texto
import re

def normalize_text(text: str) -> str:
    """
    Limpia el texto eliminando espacios duplicados, saltos de línea innecesarios y caracteres de control.
    """
    if not isinstance(text, str):
        return text
    # Reemplaza saltos de línea múltiples por uno solo
    text = re.sub(r'\n+', '\n', text)
    # Reemplaza espacios múltiples por uno solo
    text = re.sub(r'[ \t]+', ' ', text)
    # Elimina caracteres de control excepto tabulador y salto de línea
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    # Quita espacios al inicio y final
    return text.strip()
"""
Módulo para cargar y extraer texto/metadatos de documentos soportados por el crawler.
- HTML: BeautifulSoup
- DOCX: python-docx
- XLSX: openpyxl
- PDF: PyMuPDF (fitz)
"""
import os
from typing import Dict, Any

# HTML
from bs4 import BeautifulSoup

def parse_html(content: str, url: str = None) -> Dict[str, Any]:
    """
    Extrae texto y metadatos básicos de HTML.
    :param content: HTML como string
    :return: dict con 'text' y 'metadata'
    """
    try:
        soup = BeautifulSoup(content, "html.parser")
        # Heurística: priorizar main, luego article, luego section, luego body, luego bloque más largo
        candidates = []
        for tag in ["main", "article", "section"]:
            el = soup.find(tag)
            if el and el.get_text(strip=True):
                candidates.append(el.get_text(separator=" ", strip=True))
        if not candidates and soup.body:
            candidates.append(soup.body.get_text(separator=" ", strip=True))
        # Si no hay nada, usar el bloque de texto más largo
        if not candidates:
            blocks = [b.get_text(separator=" ", strip=True) for b in soup.find_all(True) if b.get_text(strip=True)]
            if blocks:
                candidates.append(max(blocks, key=len))
        text = candidates[0] if candidates else ""
        title = soup.title.string if soup.title else None
        metadata = {
            "title": title,
            "author": None,
            "date": None,
            "version": None,
            "type": "html",
            "url": url,
            "domain": None
        }
        return {
            "text": text,
            "metadata": metadata
        }
    except Exception as e:
        return {"error": str(e), "text": None, "metadata": None}

# DOCX
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

def parse_docx(path: str, url: str = None) -> Dict[str, Any]:
    """
    Extrae texto de un archivo Word (.docx).
    :param path: ruta al archivo docx
    :return: dict con 'text' y 'metadata'
    """
    if not DOCX_AVAILABLE:
        return {"error": "python-docx no está instalado", "text": None, "metadata": None}
    try:
        doc = docx.Document(path)
        text = "\n".join([p.text for p in doc.paragraphs])
        props = doc.core_properties
        metadata = {
            "title": getattr(props, "title", None),
            "author": getattr(props, "author", None),
            "date": getattr(props, "created", None),
            "version": getattr(props, "version", None) if hasattr(props, "version") else None,
            "type": "docx",
            "url": url,
            "domain": None
        }
        return {"text": text, "metadata": metadata}
    except Exception as e:
        return {"error": str(e), "text": None, "metadata": None}

# XLSX
try:
    import openpyxl
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False

def parse_xlsx(path: str, url: str = None) -> Dict[str, Any]:
    """
    Extrae texto de un archivo Excel (.xlsx).
    :param path: ruta al archivo xlsx
    :return: dict con 'text' y 'metadata'
    """
    if not XLSX_AVAILABLE:
        return {"error": "openpyxl no está instalado", "text": None, "metadata": None}
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        text = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                text.append("\t".join([str(cell) if cell is not None else '' for cell in row]))
        metadata = {
            "title": None,
            "author": None,
            "date": None,
            "version": None,
            "type": "xlsx",
            "url": url,
            "domain": None,
            "sheets": wb.sheetnames
        }
        return {"text": "\n".join(text), "metadata": metadata}
    except Exception as e:
        return {"error": str(e), "text": None, "metadata": None}

# PDF
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def parse_pdf(path: str, url: str = None) -> Dict[str, Any]:
    """
    Extrae texto de un archivo PDF usando PyMuPDF.
    :param path: ruta al archivo PDF
    :return: dict con 'text' y 'metadata'
    """
    if not PDF_AVAILABLE:
        return {"error": "PyMuPDF (fitz) no está instalado", "text": None, "metadata": None}
    try:
        doc = fitz.open(path)
        text = "\n".join(page.get_text() for page in doc)
        metadata = doc.metadata
        meta = {
            "title": metadata.get("title"),
            "author": metadata.get("author"),
            "date": metadata.get("creationDate"),
            "version": metadata.get("version", None),
            "type": "pdf",
            "url": url,
            "domain": None
        }
        return {"text": text, "metadata": meta}
    except Exception as e:
        return {"error": str(e), "text": None, "metadata": None}
# Función general para seleccionar parser según extensión
def parse_document(path: str, url: str = None) -> dict:
    """
    Selecciona el parser adecuado según la extensión del archivo.
    :param path: ruta al archivo
    :param url: url original del documento (opcional)
    :return: dict con 'text', 'metadata' o 'error'
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in [".html", ".htm"]:
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            return parse_html(content, url=url)
        except Exception as e:
            return {"error": str(e), "text": None, "metadata": None}
    elif ext == ".docx":
        return parse_docx(path, url=url)
    elif ext == ".xlsx":
        return parse_xlsx(path, url=url)
    elif ext == ".pdf":
        return parse_pdf(path, url=url)
    else:
        return {"error": f"Formato no soportado: {ext}", "text": None, "metadata": None}
