"""
Script de prueba para chunking y detección de duplicados/cambios usando hashing persistente.
Ejecuta varias veces para ver cómo cambia el estado de los chunks.
"""
from meribot.crawler.document_loader import semantic_chunk_text, process_and_classify_chunks

# Texto de ejemplo (puedes modificarlo y volver a ejecutar para ver el efecto)
texto = """
Este es un documento de prueba. Contiene varias frases para simular un texto real.
Si modificas este texto y vuelves a ejecutar el script, verás que los chunks cambian de estado.
La detección de duplicados y cambios funciona usando hashes persistentes.
"""

# Metadatos de ejemplo
metadata = {"id": "doc_test", "url": "http://localhost/doc_test"}

# Chunking
chunks = semantic_chunk_text(texto, max_chunk_size=80, min_chunk_size=30)
metadata_list = [{**metadata, "chunk_idx": i} for i in range(len(chunks))]

# Clasificación de chunks
resultados = process_and_classify_chunks(chunks, metadata_list)

# Mostrar resultados
for chunk, meta, estado in resultados:
    print(f"Chunk {meta['chunk_idx']} ({meta.get('id') or meta.get('url')}): {estado}")
    print(f"  Texto: {chunk[:60]}{'...' if len(chunk) > 60 else ''}\n")
