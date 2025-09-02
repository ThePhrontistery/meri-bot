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

    def similarity_search(self, collection_name: str, query_text: str, top_k: int = 5, where: dict = None, domains=None):
        """
        Realiza una búsqueda por similitud textual (no embeddings) en la colección indicada.
        Puede usar la función nativa de ChromaDB si existe, o realizar una búsqueda simple por substring.
        :param collection_name: Nombre de la colección en ChromaDB.
        :param query_text: Texto de consulta.
        :param top_k: Número de resultados a devolver.
        :param where: Filtro opcional por metadatos.
        :param domains: Lista de dominios para filtrar resultados.
        :return: Lista de fragmentos relevantes (dicts con metadatos y score).
        """
        # Construir filtro para dominios si se proporcionan
        if domains:
            where = where or {}
            where['dominio'] = {'$in': domains}
        collection = self.get_collection(collection_name)
        # Obtener todos los documentos de la colección
        all_docs = collection.get(include=['documents', 'metadatas', 'ids'])
        hits = []
        for i, doc in enumerate(all_docs['documents']):
            # Similitud simple: conteo de palabras compartidas (puedes mejorar con TF-IDF, fuzzy, etc.)
            score = 0
            if doc and query_text:
                doc_words = set(str(doc).lower().split())
                query_words = set(query_text.lower().split())
                score = len(doc_words & query_words)
            # Filtrado por metadatos
            meta = all_docs['metadatas'][i] if all_docs.get('metadatas') else None
            if where:
                match = True
                for k, v in where.items():
                    if meta is None or (k not in meta) or (isinstance(v, dict) and '$in' in v and meta[k] not in v['$in']) or (not isinstance(v, dict) and meta[k] != v):
                        match = False
                        break
                if not match:
                    continue
            hits.append({
                'id': all_docs['ids'][i],
                'document': doc,
                'score': score,
                'metadatas': meta
            })
        # Ordenar por score descendente y devolver los top_k
        hits = sorted(hits, key=lambda x: x['score'], reverse=True)[:top_k]
        return hits

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


    def search(self, message, domains=None, metadata=None, top_k=5):
        """
        Realiza búsqueda por similitud textual usando similarity_search de ChromaDBConnector.
        """
        results = self.chroma_connector.similarity_search(
            collection_name=self.collection_name,
            query_text=message,
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
