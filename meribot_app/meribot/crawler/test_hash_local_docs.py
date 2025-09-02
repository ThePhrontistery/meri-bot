from meribot.services.storage.chroma_integration import upsert_chunks_to_chroma
"""
Script para procesar todos los documentos de Local_C&CA_host_web,
extraer texto, hacer chunking y clasificar cambios/duplicados.
"""
import os
from meribot.crawler.document_loader import parse_document, chunk_text_with_langchain, process_and_classify_chunks

# Directorio con los documentos
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/scraped'))

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
        chunks = chunk_text_with_langchain(text, chunk_size=800, chunk_overlap=50)
        metadata_list = [{**metadata, "chunk_idx": i} for i in range(len(chunks))]
        resultados = process_and_classify_chunks(chunks, metadata_list)
        for chunk, meta, estado in resultados:
            print(f"  Chunk {meta['chunk_idx']}: {estado} | {chunk[:80]}{'...' if len(chunk) > 80 else ''}")

        # --- Guardar en ChromaDB los chunks usando LangChain ---
        # Con LangChain, no necesitamos generar embeddings manualmente
        ids = [f"{metadata['id']}_chunk_{i}" for i in range(len(chunks))]
        print(f"[DEBUG-UP] Chunks: {len(chunks)}, Ids: {len(ids)}, Metadatas: {len(metadata_list)}")
        
        if len(chunks) != len(ids) or len(chunks) != len(metadata_list):
            print(f"[ERROR] Desajuste de longitudes: chunks={len(chunks)}, ids={len(ids)}, metadatas={len(metadata_list)}")
            continue
            
        for i in range(min(3, len(chunks))):
            print(f"  Ejemplo {i+1}: id={ids[i]}, texto={chunks[i][:60]}... metadatos={metadata_list[i]}")
        
        # Usar la nueva función que funciona con LangChain
        success = upsert_chunks_to_chroma(chunks, [], metadata_list, ids, persist_dir="chroma_data")
        
        if success:
            print("[SUCCESS] Chunks almacenados exitosamente en ChromaDB usando LangChain")
            
            # Probar consulta de similitud
            from meribot.services.storage.chroma_integration import query_similar_chunks
            query_results = query_similar_chunks("EXPERTISE LEVELS MAP", n_results=3, persist_dir="chroma_data")
            
            if query_results:
                print(f"[QUERY-TEST] Resultados de consulta de similitud ({len(query_results)} encontrados):")
                for i, result in enumerate(query_results):
                    print(f"  {i+1}: Score={result['score']:.4f} | Texto={result['document'][:60]}...")
            else:
                print("[WARNING] No se pudieron realizar consultas de similitud")
        else:
            print("[ERROR] Falló el almacenamiento en ChromaDB")

if __name__ == "__main__":
    main()
