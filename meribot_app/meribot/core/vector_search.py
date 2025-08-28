# --- Stub para integración con ChatEngine/tests ---
class VectorSearch:
    """Stub de VectorSearch para integración básica y evitar errores de importación."""
    def search(self, message, domain=None, metadata=None):
        # Retorna una lista vacía por defecto (mock minimalista)
        return []

from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None
    Settings = None

class ChromaDBConnector:

    def semantic_search(self, collection_name: str, query_embedding: list, top_k: int = 5, where: dict = None):
        """
        Realiza una búsqueda semántica en la colección indicada usando un embedding.
        Permite filtrar resultados por dominio u otros metadatos usando el parámetro 'where'.

        :param collection_name: Nombre de la colección en ChromaDB.
        :param query_embedding: Vector embedding de la consulta.
        :param top_k: Número de resultados a devolver.
        :param where: Filtro opcional por metadatos (por ejemplo: {'dominio': 'soporte', 'fuente': 'intranet'}).
        :return: Lista de fragmentos relevantes (dicts con metadatos y distancia).
        """
        collection = self.get_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where or {}
        )
        # Formatear resultados para devolver fragmentos y metadatos
        hits = []
        for i in range(len(results['ids'][0])):
            hit = {
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'distance': results['distances'][0][i],
                'metadatas': results['metadatas'][0][i] if results.get('metadatas') else None
            }
            hits.append(hit)
        return hits

# Ejemplo de uso de filtrado:
# connector = ChromaDBConnector(...)
# results = connector.semantic_search(
#     collection_name="documentos",
#     query_embedding=[...],
#     top_k=5,
#     where={"dominio": "soporte", "fuente": "intranet"}
# )

# Ejemplo de citación de fuentes en la respuesta:
# for hit in results:
#     fuente = hit['metadatas'].get('fuente') if hit['metadatas'] else None
#     url = hit['metadatas'].get('url') if hit['metadatas'] else None
#     print(f"Fragmento: {hit['document']}\nFuente: {fuente or url}")

# Se recomienda que la capa de respuesta del Core incluya siempre los campos de metadatos relevantes (fuente, url, documento, etc.)
    """
    Clase para gestionar la conexión con ChromaDB.
    Permite inicializar el cliente y acceder a colecciones.
    """
    def __init__(self, persist_directory: Optional[str] = None, host: Optional[str] = None, port: Optional[int] = None):
        if chromadb is None:
            raise ImportError("El paquete 'chromadb' no está instalado. Instálalo con 'pip install chromadb'.")
        self.persist_directory = persist_directory
        self.host = host
        self.port = port
        self.client = self._init_client()

    def _init_client(self):
        """
        Inicializa el cliente de ChromaDB con configuración opcional.
        """
        settings = {}
        if self.persist_directory:
            settings['persist_directory'] = self.persist_directory
        if self.host:
            settings['host'] = self.host
        if self.port:
            settings['port'] = self.port
        return chromadb.Client(Settings(**settings)) if settings else chromadb.Client()

    def get_collection(self, name: str):
        """
        Obtiene una colección de ChromaDB por nombre.
        :param name: Nombre de la colección.
        :return: Colección de ChromaDB.
        """
        return self.client.get_or_create_collection(name)

# Ejemplo de uso:
# connector = ChromaDBConnector(persist_directory="./chroma_data")
# collection = connector.get_collection("documentos")
# print(collection.count())
