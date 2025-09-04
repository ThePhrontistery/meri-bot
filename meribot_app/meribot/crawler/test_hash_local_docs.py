
import argparse
import yaml
try:
    from meribot.services.storage.chroma_integration import upsert_chunks_to_chroma
except ImportError:
    # fallback para ejecución directa, si el import falla
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from meribot.services.storage.chroma_integration import upsert_chunks_to_chroma

"""
Script para procesar todos los documentos de Local_C&CA_host_web,
extraer texto, hacer chunking y clasificar cambios/duplicados.
"""
import os
try:
    from meribot.crawler.document_loader import parse_document, chunk_text_with_langchain, process_and_classify_chunks
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from meribot.crawler.document_loader import parse_document, chunk_text_with_langchain, process_and_classify_chunks

# Directorio con los documentos descargados
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/scraped/cca.capgemini.com'))

# Extensiones soportadas por parse_document
EXTS = {'.pdf', '.html', '.htm', '.docx', '.xlsx'}


def main():
    parser = argparse.ArgumentParser(description="Procesa documentos descargados y los ingesta en ChromaDB")
    parser.add_argument('--url', required=True, help='URL desde donde se descargan los documentos')
    parser.add_argument('--domain', required=True, help='Dominio a procesar')
    args = parser.parse_args()

    # Validar parámetros
    if not args.url.strip():
        print('[ERROR] El parámetro url es obligatorio.')
        return
    if not args.domain.strip():
        print('[ERROR] El parámetro domain es obligatorio.')
        return

    # Leer allowed_domains desde crawler_config.yaml
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crawler_config.yaml'))
    if not os.path.exists(config_path):
        print(f'[ERROR] No se encontró el archivo de configuración: {config_path}')
        return
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    allowed_domains = set(config.get('allowed_domains', []))
    if args.domain not in allowed_domains:
        print(f'[ERROR] domain no válido: {args.domain}. Allowed: {allowed_domains}')
        return

    # Usar la URL para descargar los documentos
    print(f"Procesando documentos en: {DOCS_DIR}")
    if not os.path.exists(DOCS_DIR):
        print(f"[INFO] El directorio de documentos no existe. Creando: {DOCS_DIR}")
        os.makedirs(DOCS_DIR, exist_ok=True)

    archivos_encontrados = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in EXTS:
                archivos_encontrados.append(os.path.join(root, fname))

    if not archivos_encontrados:
        print(f"[INFO] No se encontraron archivos soportados ({EXTS}) en {DOCS_DIR}. Ejecutando scraping...")
        import subprocess
        result = subprocess.run([
            "python", "-m", "meribot.meri-cli.main", "scrape",
            "--url", args.url,
            "--output", DOCS_DIR
        ], cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')), capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        # Reintentar búsqueda de archivos soportados
        archivos_encontrados = []
        for root, dirs, files in os.walk(DOCS_DIR):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in EXTS:
                    archivos_encontrados.append(os.path.join(root, fname))
        if not archivos_encontrados:
            print(f"[ERROR] No se encontraron archivos soportados ({EXTS}) en {DOCS_DIR} tras el scraping.")
            return

    for fpath in archivos_encontrados:
        rel_path = os.path.relpath(fpath, DOCS_DIR)
        doc_id = rel_path.replace(os.sep, '_')
        print(f"\nProcesando: {rel_path}")
        try:
            doc = parse_document(fpath, url=rel_path)
        except Exception as e:
            print(f"  [ERROR] Falló la extracción del documento: {e}")
            continue
        if doc.get('error') or not doc.get('text'):
            print(f"  [ERROR] Sin texto extraído o error: {doc.get('error')}")
            continue
        text = doc['text']
        print(f"  Texto extraído (primeros 300 chars):\n{text[:300]}{'...' if len(text) > 300 else ''}\n")
        if not text.strip() or len(text.strip()) < 20:
            print("  [ADVERTENCIA] El texto extraído está vacío o es demasiado corto. Se omite el chunking.\n")
            continue
        metadata = doc.get('metadata', {})
        metadata['id'] = doc_id
        metadata['source_path'] = rel_path
        metadata['domain'] = args.domain
        try:
            chunks = chunk_text_with_langchain(text, chunk_size=800, chunk_overlap=50)
        except Exception as e:
            print(f"  [ERROR] Falló el chunking: {e}")
            continue
        metadata_list = [{**metadata, "chunk_idx": i} for i in range(len(chunks))]
        try:
            resultados = process_and_classify_chunks(chunks, metadata_list)
        except Exception as e:
            print(f"  [ERROR] Falló la clasificación de chunks: {e}")
            continue
        for chunk, meta, estado in resultados:
            print(f"  Chunk {meta['chunk_idx']}: {estado} | {chunk[:80]}{'...' if len(chunk) > 80 else ''}")

        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        print(f"[DEBUG-UP] Chunks: {len(chunks)}, Ids: {len(ids)}, Metadatas: {len(metadata_list)}")

        if len(chunks) != len(ids) or len(chunks) != len(metadata_list):
            print(f"[ERROR] Desajuste de longitudes: chunks={len(chunks)}, ids={len(ids)}, metadatas={len(metadata_list)}")
            continue

        for i in range(min(3, len(chunks))):
            print(f"  Ejemplo {i+1}: id={ids[i]}, texto={chunks[i][:60]}... metadatos={metadata_list[i]}")

        try:
            success = upsert_chunks_to_chroma(chunks, [], metadata_list, ids, persist_dir="chroma_data")
        except Exception as e:
            print(f"[ERROR] Falló el almacenamiento en ChromaDB: {e}")
            continue

        if success:
            print("[SUCCESS] Chunks almacenados exitosamente en ChromaDB usando LangChain")
            try:
                from meribot.services.storage.chroma_integration import query_similar_chunks
                query_results = query_similar_chunks("EXPERTISE LEVELS MAP", n_results=3, persist_dir="chroma_data")
                if query_results:
                    print(f"[QUERY-TEST] Resultados de consulta de similitud ({len(query_results)} encontrados):")
                    for i, result in enumerate(query_results):
                        print(f"  {i+1}: Score={result['score']:.4f} | Texto={result['document'][:60]}...")
                else:
                    print("[WARNING] No se pudieron realizar consultas de similitud")
            except Exception as e:
                print(f"[ERROR] Falló la consulta de similitud: {e}")
        else:
            print("[ERROR] Falló el almacenamiento en ChromaDB")

if __name__ == "__main__":
    main()
