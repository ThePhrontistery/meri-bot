########################################
# Chunking semántico configurable
from typing import List, Optional
import numpy as np
try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None
    util = None

def semantic_chunk_text(
    text: str,
    model_name: str = "all-MiniLM-L6-v2",
    max_chunk_size: int = 500,
    min_chunk_size: int = 200,
    stride: int = 50,
    split_on_newline: bool = True,
    similarity_threshold: float = 0.7,
    return_embeddings: bool = False
) -> List[str]:
    """
    Divide el texto en fragmentos semánticamente coherentes usando embeddings.
    Usa SentenceTransformer para calcular similitud entre frases y agruparlas en chunks.

    Args:
        text (str): Texto a fragmentar.
        model_name (str): Nombre del modelo de embeddings.
        max_chunk_size (int): Máximo de caracteres por chunk.
        min_chunk_size (int): Mínimo de caracteres por chunk.
        stride (int): Superposición de caracteres entre chunks.
        split_on_newline (bool): Si True, divide primero por saltos de línea.
        similarity_threshold (float): Umbral de similitud para unir frases.
        return_embeddings (bool): Si True, retorna tuplas (chunk, embedding).

    Returns:
        List[str] o List[Tuple[str, np.ndarray]]: Lista de chunks (y opcionalmente embeddings).
    """
    if SentenceTransformer is None or util is None:
        raise ImportError("sentence-transformers no está instalado. Instala con 'pip install sentence-transformers'.")

    if split_on_newline:
        sentences = [s.strip() for s in text.split("\n") if s.strip()]
    else:
        # Simple sentence split (could be improved)
        import re
        sentences = re.split(r'(?<=[.!?]) +', text)
        sentences = [s.strip() for s in sentences if s.strip()]

    model = SentenceTransformer(model_name)
    embeddings = model.encode(sentences, convert_to_tensor=True)

    chunks = []
    current_chunk = []
    current_len = 0
    for i, (sent, emb) in enumerate(zip(sentences, embeddings)):
        if not current_chunk:
            current_chunk.append(sent)
            current_len = len(sent)
            last_emb = emb
            continue
        sim = float(util.cos_sim(emb, last_emb))
        if (current_len + len(sent) <= max_chunk_size and sim >= similarity_threshold) or current_len < min_chunk_size:
            current_chunk.append(sent)
            current_len += len(sent)
            last_emb = emb
        else:
            chunk_text = " ".join(current_chunk)
            chunks.append(chunk_text)
            # Start new chunk, with stride overlap if needed
            if stride > 0 and len(current_chunk) > 1:
                overlap = current_chunk[-stride:] if stride < len(current_chunk) else current_chunk
                current_chunk = list(overlap)
                current_len = sum(len(s) for s in current_chunk)
            else:
                current_chunk = [sent]
                current_len = len(sent)
            last_emb = emb
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append(chunk_text)

    if return_embeddings:
        chunk_embs = model.encode(chunks, convert_to_tensor=True)
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
