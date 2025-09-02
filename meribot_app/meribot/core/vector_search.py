import os
import requests
from typing import Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None
    Settings = None

class ChromaDBConnector:

    def semantic_search(self, collection_name: str, query_embedding: list, top_k: int = 5, where: dict = None, domains=None):
        """
        Realiza una búsqueda semántica en la colección indicada usando un embedding.
        Permite filtrar resultados por dominio u otros metadatos usando el parámetro 'where'.
        Si domains es una lista, se filtra por todos los dominios recibidos (OR).

        :param collection_name: Nombre de la colección en ChromaDB.
        :param query_embedding: Vector embedding de la consulta.
        :param top_k: Número de resultados a devolver.
        :param where: Filtro opcional por metadatos (por ejemplo: {'dominio': 'soporte', 'fuente': 'intranet'}).
        :param domains: Lista de dominios para filtrar resultados.
        :return: Lista de fragmentos relevantes (dicts con metadatos y distancia).
        """
        # Construir filtro para dominios si se proporcionan
        if domains:
            where = where or {}
            where['dominio'] = {'$in': domains}
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

class VectorSearch:
    """Implementación real de VectorSearch usando Azure OpenAI para embeddings y ChromaDB para búsqueda semántica."""
    def __init__(self, collection_name: str = None, chroma_connector: 'ChromaDBConnector' = None):
        self.collection_name = collection_name or os.getenv('CHROMADB_COLLECTION', 'documentos')
        self.chroma_connector = chroma_connector or ChromaDBConnector()
        self.openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.openai_deployment = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT')
        self.openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')

    def get_embedding(self, text: str) -> list:
        """
        Obtiene el embedding del texto usando Azure OpenAI Embeddings API.
        """
        url = f"{self.openai_endpoint}openai/deployments/{self.openai_deployment}/embeddings?api-version={self.openai_api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.openai_api_key
        }
        data = {"input": text}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        embedding = response.json()["data"][0]["embedding"]
        return embedding

    def search(self, message, domains=None, metadata=None, top_k=5):
        """
        Realiza búsqueda semántica en ChromaDB usando el embedding del mensaje y filtrando por dominios.
        """
        embedding = self.get_embedding(message)
        results = self.chroma_connector.semantic_search(
            collection_name=self.collection_name,
            query_embedding=embedding,
            top_k=top_k,
            where=metadata,
            domains=domains
        )
        return results

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
