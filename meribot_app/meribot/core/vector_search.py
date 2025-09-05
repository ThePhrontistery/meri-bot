import os
from typing import Optional
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings


def build_embeddings(azure_deployment: str, api_version: str | None, azure_endpoint: str | None):
    """Crea el cliente de embeddings de Azure OpenAI (usa AZURE_OPENAI_API_KEY del entorno)."""
    return AzureOpenAIEmbeddings(
        azure_deployment=azure_deployment,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
    )


def connect_store(persist_dir: str, collection: str, embeddings):
    """Conecta con Chroma usando LangChain."""
    return Chroma(
        collection_name=collection,
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )


class ChromaDBConnector:
    """
    Clase para gestionar la conexión con ChromaDB usando LangChain y Azure OpenAI Embeddings.
    """
    def __init__(self, persist_directory: Optional[str] = None, collection_name: Optional[str] = None):
        self.persist_directory = persist_directory or os.path.join(os.path.dirname(__file__), '../../chroma_data')
        self.collection_name = "meri_chunks"
        self.openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.openai_deployment = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT')
        self.openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
        self.embeddings = build_embeddings(
            azure_deployment=self.openai_deployment,
            api_version=self.openai_api_version,
            azure_endpoint=self.openai_endpoint,
        )
        self.store = connect_store(
            persist_dir=self.persist_directory,
            collection=self.collection_name,
            embeddings=self.embeddings,
        )

    def similarity_search(self, query_text: str, top_k: int = 5, where: dict = None, domains=None):
        """
        Realiza una búsqueda por similitud textual usando LangChain Chroma.
        """
        # Construir filtro para dominios si se proporcionan
        if domains:
            where = where or {}
            where['domain'] = {'$in': domains}
        # LangChain Chroma no soporta filtro directo por metadatos en similarity_search, así que filtramos después
        results = self.store.similarity_search(query_text, k=top_k)
        print("-------------------------------")
        print(f"Resultados encontrados:", results)
        hits = []
        for doc in results:
            meta = doc.metadata if hasattr(doc, 'metadata') else None
            if where:
                match = True
                for k, v in where.items():
                    if meta is None or (k not in meta) or (isinstance(v, dict) and '$in' in v and meta[k] not in v['$in']) or (not isinstance(v, dict) and meta[k] != v):
                        match = False
                        break
                if not match:
                    continue
            hits.append({
                'id': getattr(doc, 'id', None),
                'document': doc.page_content if hasattr(doc, 'page_content') else str(doc),
                'score': None,  # LangChain no devuelve score en similarity_search
                'metadatas': meta
            })
        print("-------------------------------")
        print(f"Resultados filtrados:", hits)
        return hits[:top_k]

    def semantic_search(self, query_text: str, top_k: int = 5, where: dict = None, domains=None):
        """
        Realiza una búsqueda semántica usando embeddings y LangChain Chroma.
        """
        # Construir filtro para dominios si se proporcionan
        if domains:
            where = where or {}
            where['domain'] = {'$in': domains}
        # LangChain Chroma no soporta filtro directo por metadatos en similarity_search, así que filtramos después
        results = self.store.similarity_search(query_text, k=top_k)
        hits = []
        for doc in results:
            meta = doc.metadata if hasattr(doc, 'metadata') else None
            if where:
                match = True
                for k, v in where.items():
                    if meta is None or (k not in meta) or (isinstance(v, dict) and '$in' in v and meta[k] not in v['$in']) or (not isinstance(v, dict) and meta[k] != v):
                        match = False
                        break
                if not match:
                    continue
            hits.append({
                'id': getattr(doc, 'id', None),
                'document': doc.page_content if hasattr(doc, 'page_content') else str(doc),
                'distance': None,  # LangChain no devuelve distancia explícita
                'metadatas': meta
            })
        return hits[:top_k]


class VectorSearch:
    """Implementación real de VectorSearch usando Azure OpenAI para embeddings y ChromaDB para búsqueda semántica."""
    def __init__(self, collection_name: str = None, chroma_connector: 'ChromaDBConnector' = None):
        self.collection_name = "meri_chunks"
        self.chroma_connector = chroma_connector or ChromaDBConnector(collection_name=self.collection_name)

    def search(self, message, domains=None, metadata=None, top_k=5):
        """
        Realiza búsqueda por similitud textual usando similarity_search de ChromaDBConnector.
        """
        results = self.chroma_connector.similarity_search(
            query_text=message,
            top_k=top_k,
            where=metadata,
            domains=domains
        )
        return results

    def semantic_search(self, message, domains=None, metadata=None, top_k=5):
        """
        Realiza búsqueda semántica usando embeddings y LangChain Chroma.
        """
        results = self.chroma_connector.semantic_search(
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
