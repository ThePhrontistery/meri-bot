import os
from typing import Optional
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from meribot.utils.logger import get_logger

class ChromaDBConnector:
    """
    Gestiona la conexión con ChromaDB y Azure OpenAI Embeddings.
    """
    def __init__(self):
        self.logger = get_logger("meribot.chroma.connector", log_file=os.getenv("MERIBOT_LOG_FILE"))
        # Siempre recoger persist_directory y collection_name desde el entorno
        env_persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY')
        self.persist_directory = env_persist_dir or 'chroma_data'
        self.collection_name = os.getenv('CHROMA_COLLECTION_NAME')
        self.openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.openai_deployment = os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT')
        self.openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        self.logger.info(f"Inicializando ChromaDBConnector con persist_directory={self.persist_directory}, collection_name={self.collection_name}")
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
        self.logger.info("ChromaDBConnector inicializado correctamente.")

    def similarity_search(self, query_text: str, top_k: int = 5, where: dict = None, domains=None):
        """
        Búsqueda por similitud textual usando LangChain Chroma.
        Filtra por dominios si se proporcionan.
        """
        self.logger.info(f"Realizando similarity_search: top_k={top_k}, domains={domains}")
        if domains:
            where = where or {}
            where['domain'] = {'$in': domains}
        try:
            results = self.store.similarity_search(query_text, k=top_k)
        except Exception as e:
            self.logger.error(f"Error en similarity_search: {e}")
            raise
        self.logger.debug("---- METADATAS DE DOCUMENTOS EXTRAÍDOS ----")
        for doc in results:
            self.logger.debug(getattr(doc, 'metadata', None))
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
