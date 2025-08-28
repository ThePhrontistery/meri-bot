def test_insert_and_query(persist_dir="chroma_data"):
    print("[TEST] Insertando y consultando datos de ejemplo en ChromaDB...")
    from meribot.services.storage.chroma_integration import get_chroma_collection
    collection = get_chroma_collection("test_collection", persist_dir=persist_dir)
    ids = ["test1", "test2"]
    docs = ["Este es un fragmento de prueba uno.", "Este es un fragmento de prueba dos."]
    embeddings = [[0.1]*10, [0.2]*10]
    metadatas = [{"source": "test"}, {"source": "test"}]
    collection.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metadatas)
    print("[TEST] Upsert realizado. Consultando...")
    results = collection.get()
    print(f"[TEST] Recuperados: {len(results.get('ids', []))}")
    for i, (id_, doc, meta) in enumerate(zip(results.get('ids', []), results.get('documents', []), results.get('metadatas', []))):
        print(f"  {i+1}: ID={id_} | Texto={doc} | Metadatos={meta}")
import chromadb
from chromadb.config import Settings
def list_collections(persist_dir="chroma_data"):
    print(f"[DEBUG] Listando colecciones en persist_dir='{persist_dir}'...")
    client = chromadb.Client(Settings(persist_directory=persist_dir))
    collections = client.list_collections()
    for col in collections:
        print(f"Colección: {col.name} | N° fragmentos: {col.count()} | Metadata: {col.metadata}")

"""
Script para consultar y listar los fragmentos almacenados en ChromaDB.
"""
from meribot.services.storage.chroma_integration import get_chroma_collection


COLLECTION_NAME = "meri_chunks"
PERSIST_DIR = "chroma_data"


def main():
    print(f"[DEBUG] Consultando ChromaDB: collection='{COLLECTION_NAME}', persist_dir='{PERSIST_DIR}'")
    collection = get_chroma_collection(COLLECTION_NAME, persist_dir=PERSIST_DIR)
    # Recupera los primeros 10 fragmentos almacenados
    results = collection.get(limit=10)
    ids = results.get("ids", [])
    docs = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    print(f"Total recuperados: {len(ids)}\n")
    for i, (id_, doc, meta) in enumerate(zip(ids, docs, metadatas)):
        print(f"Fragmento {i+1}:")
        print(f"  ID: {id_}")
        print(f"  Texto: {doc[:120]}{'...' if len(doc) > 120 else ''}")
        print(f"  Metadatos: {meta}")
        print()

if __name__ == "__main__":
    list_collections(persist_dir=PERSIST_DIR)
    print("\n---\n")
    test_insert_and_query(persist_dir=PERSIST_DIR)
    print("\n---\n")
    main()
