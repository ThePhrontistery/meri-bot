"""
Módulo para cargar y extraer texto/metadatos de documentos soportados por el crawler.
- HTML: BeautifulSoup
- DOCX: python-docx
- XLSX: openpyxl
- PDF: PyMuPDF (fitz)
"""
from typing import Dict, Any

# HTML
from bs4 import BeautifulSoup

def parse_html(content: str) -> Dict[str, Any]:
    """
    Extrae texto y metadatos básicos de HTML.
    :param content: HTML como string
    :return: dict con 'text' y 'metadata'
    """
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    title = soup.title.string if soup.title else None
    return {
        "text": text,
        "metadata": {"title": title}
    }

# DOCX
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

def parse_docx(path: str) -> Dict[str, Any]:
    """
    Extrae texto de un archivo Word (.docx).
    :param path: ruta al archivo docx
    :return: dict con 'text' y 'metadata'
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx no está instalado")
    doc = docx.Document(path)
    text = "\n".join([p.text for p in doc.paragraphs])
    props = doc.core_properties
    metadata = {k: getattr(props, k) for k in dir(props) if not k.startswith('_') and not callable(getattr(props, k))}
    return {"text": text, "metadata": metadata}

# XLSX
try:
    import openpyxl
    XLSX_AVAILABLE = True
except ImportError:
    XLSX_AVAILABLE = False

def parse_xlsx(path: str) -> Dict[str, Any]:
    """
    Extrae texto de un archivo Excel (.xlsx).
    :param path: ruta al archivo xlsx
    :return: dict con 'text' y 'metadata'
    """
    if not XLSX_AVAILABLE:
        raise ImportError("openpyxl no está instalado")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    text = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            text.append("\t".join([str(cell) if cell is not None else '' for cell in row]))
    return {"text": "\n".join(text), "metadata": {"sheets": wb.sheetnames}}

# PDF
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def parse_pdf(path: str) -> Dict[str, Any]:
    """
    Extrae texto de un archivo PDF usando PyMuPDF.
    :param path: ruta al archivo PDF
    :return: dict con 'text' y 'metadata'
    """
    if not PDF_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) no está instalado")
    doc = fitz.open(path)
    text = "\n".join(page.get_text() for page in doc)
    metadata = doc.metadata
    return {"text": text, "metadata": metadata}
