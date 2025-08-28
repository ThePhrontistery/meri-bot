"""
Módulo de integración básica con ChromaDB para almacenamiento de fragmentos.
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

# Inicializa el cliente y la colección (persistente en disco)
def get_chroma_collection(collection_name="meri_chunks", persist_dir="chroma_data"):
    print(f"[DEBUG] Conectando a ChromaDB: collection='{collection_name}', persist_dir='{persist_dir}'")
    client = chromadb.Client(Settings(persist_directory=persist_dir))
    collection = client.get_or_create_collection(collection_name)
    return collection

# Inserta fragmentos (chunks) en la colección
# embeddings: lista de vectores (uno por chunk)
# metadatas: lista de dicts (uno por chunk)
def upsert_chunks_to_chroma(chunks: List[str], embeddings: List[list], metadatas: List[Dict[str, Any]], ids: List[str], collection_name="meri_chunks", persist_dir="chroma_data"):
    collection = get_chroma_collection(collection_name, persist_dir=persist_dir)
    print(f"[DEBUG] Upserting {len(chunks)} chunks en ChromaDB...")
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )
    print(f"Upserted {len(chunks)} chunks en ChromaDB.")
