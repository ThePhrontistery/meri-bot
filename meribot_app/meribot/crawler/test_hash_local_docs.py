"""
Script para procesar todos los documentos de Local_C&CA_host_web,
extraer texto, hacer chunking y clasificar cambios/duplicados.
"""
import os
from meribot.crawler.document_loader import parse_document, semantic_chunk_text, process_and_classify_chunks

# Directorio con los documentos
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../Local_C&CA_host_web'))

# Extensiones soportadas por parse_document
EXTS = {'.pdf', '.html', '.htm', '.docx', '.xlsx'}

def main():
    for fname in os.listdir(DOCS_DIR):
        fpath = os.path.join(DOCS_DIR, fname)
        ext = os.path.splitext(fname)[1].lower()
        if not os.path.isfile(fpath) or ext not in EXTS:
            continue
        print(f"\nProcesando: {fname}")
        doc = parse_document(fpath, url=fname)
        if doc.get('error') or not doc.get('text'):
            print(f"  Error o sin texto extraído: {doc.get('error')}")
            continue
        text = doc['text']
        print(f"  Texto extraído (primeros 300 chars):\n{text[:300]}{'...' if len(text) > 300 else ''}\n")
        if not text.strip() or len(text.strip()) < 20:
            print("  [ADVERTENCIA] El texto extraído está vacío o es demasiado corto. Se omite el chunking.\n")
            continue
        metadata = doc.get('metadata', {})
        metadata['id'] = fname
        # Chunking
        chunks = semantic_chunk_text(text, max_chunk_size=800, min_chunk_size=200)
        metadata_list = [{**metadata, "chunk_idx": i} for i in range(len(chunks))]
        resultados = process_and_classify_chunks(chunks, metadata_list)
        for chunk, meta, estado in resultados:
            print(f"  Chunk {meta['chunk_idx']}: {estado} | {chunk[:80]}{'...' if len(chunk) > 80 else ''}")

if __name__ == "__main__":
    main()
