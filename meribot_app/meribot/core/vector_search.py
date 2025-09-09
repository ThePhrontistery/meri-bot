
import os
from typing import Optional
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings



class ChromaDBConnector:
    """
    Gestiona la conexión con ChromaDB y Azure OpenAI Embeddings.
    """
    def __init__(self, persist_directory: Optional[str] = None, collection_name: Optional[str] = None):
        # Inicialización de parámetros
        self.persist_directory = persist_directory or os.path.join(os.path.dirname(__file__), '../../chroma_data')
        self.collection_name = collection_name or os.getenv('CHROMA_COLLECTION_NAME')
        self.openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.openai_deployment = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT')
        self.openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        # Embeddings y store
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=self.openai_deployment,
            api_version=self.openai_api_version,
            azure_endpoint=self.openai_endpoint,
        )
        self.store = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def similarity_search(self, query_text: str, top_k: int = 5, where: dict = None, domains=None):
        """
        Búsqueda por similitud textual usando LangChain Chroma.
        Filtra por dominios si se proporcionan.
        """
        if domains:
            where = where or {}
            where['domain'] = {'$in': domains}
        results = self.store.similarity_search(query_text, k=top_k)
        print("---- METADATAS DE DOCUMENTOS EXTRAÍDOS ----")
        for doc in results:
            print(getattr(doc, 'metadata', None))
        hits = []
        for doc in results:
            meta = getattr(doc, 'metadata', None)
            match = True
            if where:
                for k, v in where.items():
                    if meta is None or (k not in meta) or (isinstance(v, dict) and '$in' in v and meta[k] not in v['$in']) or (not isinstance(v, dict) and meta[k] != v):
                        match = False
                        break
            if not match:
                continue
            hits.append({
                'id': getattr(doc, 'id', None),
                'document': getattr(doc, 'page_content', str(doc)),
                'score': None,
                'metadatas': meta
            })
        return hits[:top_k]


class VectorSearch:
    """
    Implementa VectorSearch usando Azure OpenAI y ChromaDB.
    """
    def __init__(self, collection_name: str = None, chroma_connector: 'ChromaDBConnector' = None):
        self.collection_name = collection_name or os.getenv('CHROMA_COLLECTION_NAME')
        self.chroma_connector = chroma_connector or ChromaDBConnector(collection_name=self.collection_name)

    def search(self, message, domains=None, metadata=None, top_k=5):
        """
        Búsqueda por similitud textual.
        """
        return self.chroma_connector.similarity_search(
            query_text=message,
            top_k=top_k,
            where=metadata,
            domains=domains
        )

