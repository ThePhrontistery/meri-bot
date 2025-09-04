"""
Script de prueba para document_loader.py
Prueba los parsers de HTML, DOCX, XLSX y PDF con archivos de ejemplo.
"""
from document_loader import parse_document, normalize_text, split_text, semantic_chunk_text


def test_any(path, url=None):
    result = parse_document(path, url=url)
    print(f"\n--- Resultado para: {path} ---")
    raw_text = result.get("text") or ""
    print("Texto original:", raw_text[:200], "...")
    print("Metadatos:", result.get("metadata", {}))
    # Prueba de normalización
    norm_text = normalize_text(raw_text)
    print("Texto normalizado:", norm_text[:200], "...")

    # Prueba de fragmentación tradicional
    chunks = split_text(norm_text, max_length=200)
    print(f"Fragmentos tradicionales (max 200 chars, total {len(chunks)}):")
    for i, chunk in enumerate(chunks[:3]):
        print(f"  [{i+1}] {chunk[:100]}...")
    if len(chunks) > 3:
        print(f"  ...({len(chunks)-3} fragmentos más)")

    # Prueba de fragmentación semántica
    try:
        sem_chunks = semantic_chunk_text(norm_text, max_chunk_size=200, min_chunk_size=80, stride=1, split_on_newline=True, similarity_threshold=0.6)
        print(f"Fragmentos semánticos (max 200 chars, total {len(sem_chunks)}):")
        for i, chunk in enumerate(sem_chunks[:3]):
            print(f"  [{i+1}] {chunk[:100]}...")
        if len(sem_chunks) > 3:
            print(f"  ...({len(sem_chunks)-3} fragmentos más)")
    except ImportError as e:
        print(f"[!] No se pudo probar chunking semántico: {e}")

if __name__ == "__main__":
    test_any(
        r"c:/Meri_bot/meri-bot/Local_C&CA_host_web/Cloud & Custom Applications.html",
        url="https://cca.capgemini.com/web/home"
    )
    test_any(
        r"c:/Meri_bot/meri-bot/Local_C&CA_host_web/DefinicionDeCompetenciasCCA.pdf",
        url="https://cca.capgemini.com/docs/DefinicionDeCompetenciasCCA.pdf"
    )
