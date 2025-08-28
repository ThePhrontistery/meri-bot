from meribot.services.storage.chroma_integration import upsert_chunks_to_chroma
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

        # --- Guardar en ChromaDB los chunks y embeddings ---
        # Obtener embeddings de los chunks (reutiliza la función de embeddings)
        from meribot.crawler.document_loader import get_azure_openai_embeddings
        embeddings = get_azure_openai_embeddings(chunks)
        ids = [f"{metadata['id']}_chunk_{i}" for i in range(len(chunks))]
        print(f"[DEBUG-UP] Chunks: {len(chunks)}, Embeddings: {len(embeddings)}, Ids: {len(ids)}, Metadatas: {len(metadata_list)}")
        if len(chunks) != len(embeddings) or len(chunks) != len(ids) or len(chunks) != len(metadata_list):
            print(f"[ERROR] Desajuste de longitudes: chunks={len(chunks)}, embeddings={len(embeddings)}, ids={len(ids)}, metadatas={len(metadata_list)}")
        for i in range(min(3, len(chunks))):
            print(f"  Ejemplo {i+1}: id={ids[i]}, texto={chunks[i][:60]}... metadatos={metadata_list[i]}")
        upsert_chunks_to_chroma(chunks, embeddings.tolist(), metadata_list, ids, persist_dir="chroma_data")
        # Consulta directa tras el upsert
        from meribot.services.storage.chroma_integration import get_chroma_collection_and_client
        collection, _ = get_chroma_collection_and_client("meri_chunks", persist_dir="chroma_data")
        results = collection.get(limit=5)
        print(f"[POST-UPSERT] Recuperados tras upsert: {len(results.get('ids', []))}")
        for i, (id_, doc, meta) in enumerate(zip(results.get('ids', []), results.get('documents', []), results.get('metadatas', []))):
            print(f"  {i+1}: ID={id_} | Texto={doc[:60]}... | Metadatos={meta}")

if __name__ == "__main__":
    main()
