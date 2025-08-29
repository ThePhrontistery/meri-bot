"""
Módulo de integración básica con ChromaDB para almacenamiento de fragmentos usando LangChain.
"""
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.embeddings import Embeddings
from typing import List, Dict, Any, Optional
import numpy as np
import os
from dotenv import load_dotenv

class AzureOpenAIEmbeddings(Embeddings):
    """
    Clase de embeddings personalizada para Azure OpenAI compatible con LangChain.
    """
    
    def __init__(self):
        # Cargar variables de entorno desde .env
        env_paths = [
            os.path.join(os.path.dirname(__file__), '../../crawler/.env'),
            os.path.join(os.path.dirname(__file__), '../../../.env'),
            '.env'
        ]
        
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                print(f"[DEBUG] Cargando .env desde: {env_path}")
                break
        
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
        
        if not self.endpoint or not self.api_key or not self.deployment:
            raise RuntimeError("Faltan variables de entorno para Azure OpenAI embeddings.")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de documentos."""
        return self._get_embeddings(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Genera embedding para una consulta individual."""
        return self._get_embeddings([text])[0]
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Método interno para obtener embeddings de Azure OpenAI."""
        import requests
        import json
        
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/embeddings?api-version=2023-05-15"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        data = {"input": texts}
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise RuntimeError(f"Error Azure OpenAI: {response.status_code} {response.text}")
        
        result = response.json()
        return [item["embedding"] for item in result["data"]]

# Inicializa el cliente y la colección (persistente en disco)
def get_chroma_collection_and_client(collection_name="meri_chunks", persist_dir="chroma_data"):
    """
    Inicializa y retorna una colección de ChromaDB usando LangChain.
    
    Args:
        collection_name: Nombre de la colección
        persist_dir: Directorio donde se persisten los datos
    
    Returns:
        Chroma: Objeto de vectorstore de ChromaDB
    """
    # Asegura que el directorio de persistencia exista
    if persist_dir and not os.path.exists(persist_dir):
        os.makedirs(persist_dir, exist_ok=True)
    
    print(f"[DEBUG] Conectando a ChromaDB: collection='{collection_name}', persist_dir='{persist_dir}'")
    
    # Crear instancia de embeddings
    embeddings = AzureOpenAIEmbeddings()

    # Crear o cargar el vectorstore
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir
    )
    
    return vectorstore, None  # Retornamos None como cliente para mantener compatibilidad

# Inserta fragmentos (chunks) en la colección
def upsert_chunks_to_chroma(
    chunks: List[str], 
    embeddings: List[list], 
    metadatas: List[Dict[str, Any]], 
    ids: List[str], 
    collection_name="meri_chunks", 
    persist_dir="chroma_data"
) -> bool:
    """
    Inserta o actualiza chunks con sus embeddings en ChromaDB usando LangChain.
    
    Args:
        chunks: Lista de textos de los fragmentos
        embeddings: Lista de vectores de embeddings (uno por chunk) - No se usa con LangChain
        metadatas: Lista de metadatos (uno por chunk)
        ids: Lista de identificadores únicos (uno por chunk)
        collection_name: Nombre de la colección
        persist_dir: Directorio de persistencia
    
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        # Validaciones de entrada
        if len(chunks) == 0 or len(metadatas) == 0 or len(ids) == 0:
            print("[ERROR] Alguna de las listas de entrada está vacía")
            return False
        
        # Verificar que las listas tengan la misma longitud
        lengths = [len(chunks), len(metadatas), len(ids)]
        if len(set(lengths)) != 1:
            print(f"[ERROR] Desajuste de longitudes: chunks={len(chunks)}, metadatas={len(metadatas)}, ids={len(ids)}")
            return False
        
        vectorstore, _ = get_chroma_collection_and_client(collection_name, persist_dir=persist_dir)
        print(f"[DEBUG] Upserting {len(chunks)} chunks en ChromaDB usando LangChain...")
        
        # LangChain se encarga de generar los embeddings automáticamente
        vectorstore.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        # Persistir cambios
        vectorstore.persist()
        
        print(f"[SUCCESS] Upserted {len(chunks)} chunks en ChromaDB usando LangChain.")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al insertar chunks en ChromaDB: {str(e)}")
        return False

def query_similar_chunks(
    query_text: str,
    n_results: int = 5,
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data"
) -> Optional[List[Dict[str, Any]]]:
    """
    Consulta chunks similares basados en un texto de consulta.
    
    Args:
        query_text: Texto de la consulta
        n_results: Número de resultados a retornar
        collection_name: Nombre de la colección
        persist_dir: Directorio de persistencia
    
    Returns:
        Lista de resultados con documentos y metadatos
    """
    try:
        vectorstore, _ = get_chroma_collection_and_client(collection_name, persist_dir)
        
        # Realizar búsqueda por similitud
        results = vectorstore.similarity_search_with_score(
            query_text,
            k=n_results
        )
        
        # Formatear resultados
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "document": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
        
        print(f"[DEBUG] Consulta completada. Encontrados {len(formatted_results)} resultados")
        return formatted_results
        
    except Exception as e:
        print(f"[ERROR] Error en consulta de similitud: {str(e)}")
        return None

def get_collection_stats(
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data"
) -> Optional[Dict[str, Any]]:
    """
    Obtiene estadísticas de la colección.
    
    Args:
        collection_name: Nombre de la colección
        persist_dir: Directorio de persistencia
    
    Returns:
        Dict con estadísticas de la colección
    """
    try:
        vectorstore, _ = get_chroma_collection_and_client(collection_name, persist_dir)
        
        # Con LangChain, obtenemos estadísticas haciendo una consulta
        sample_results = vectorstore.similarity_search("test", k=1)
        
        stats = {
            "collection_name": collection_name,
            "persist_dir": persist_dir,
            "has_documents": len(sample_results) > 0
        }
        
        return stats
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo estadísticas: {str(e)}")
        return None
