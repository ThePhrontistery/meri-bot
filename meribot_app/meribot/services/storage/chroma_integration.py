"""
Módulo de integración básica con ChromaDB para almacenamiento de fragmentos.
"""
import chromadb
from typing import List, Dict, Any

# Inicializa el cliente y la colección (persistente en disco)
def get_chroma_collection_and_client(collection_name="meri_chunks", persist_dir="chroma_data"):
    import os
    # Asegura que el directorio de persistencia exista
    if persist_dir and not os.path.exists(persist_dir):
        os.makedirs(persist_dir, exist_ok=True)
    print(f"[DEBUG] Conectando a ChromaDB: collection='{collection_name}', persist_dir='{persist_dir}'")
    # Usar la nueva API de ChromaDB para persistencia real en disco
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(collection_name)
    return collection, client

# Inserta fragmentos (chunks) en la colección
# embeddings: lista de vectores (uno por chunk)
# metadatas: lista de dicts (uno por chunk)
def upsert_chunks_to_chroma(chunks: List[str], embeddings: List[list], metadatas: List[Dict[str, Any]], ids: List[str], collection_name="meri_chunks", persist_dir="chroma_data"):
    collection, client = get_chroma_collection_and_client(collection_name, persist_dir=persist_dir)
    print(f"[DEBUG] Upserting {len(chunks)} chunks en ChromaDB...")
    collection.upsert(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    # Persistencia en disco: automática con PersistentClient (no se requiere client.persist())
    print(f"Upserted {len(chunks)} chunks en ChromaDB.")
