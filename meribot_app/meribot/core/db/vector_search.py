from typing import Optional
from .chromadb_connector import ChromaDBConnector

class VectorSearch:
    """
    Implementa VectorSearch usando Azure OpenAI y ChromaDB.
    """
    def __init__(self, collection_name: str = None, chroma_connector: Optional[ChromaDBConnector] = None):
        self.collection_name = collection_name
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
