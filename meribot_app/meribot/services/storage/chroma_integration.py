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
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
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

def delete_document_by_id(
    document_id: str,
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data"
) -> int:
    """
    Elimina todos los chunks asociados a un documento por su ID en ChromaDB usando LangChain.

    Args:
        document_id (str): ID del documento a borrar.
        collection_name (str): Nombre de la colección de ChromaDB.
        persist_dir (str): Directorio de persistencia de ChromaDB.

    Returns:
        int: Número de chunks eliminados.

    Raises:
        ValueError: Si no se encuentran chunks asociados al documento.
        Exception: Si ocurre un error durante el borrado.
    """
    vectorstore, _ = get_chroma_collection_and_client(collection_name=collection_name, persist_dir=persist_dir)
    # Solo se puede incluir metadatas, no ids
    all_docs = vectorstore.get(include=["metadatas"])
    chunk_ids = []
    ids_list = all_docs.get("ids", [])
    metadatas_list = all_docs.get("metadatas", [])
    for idx, meta in enumerate(metadatas_list):
        if meta and meta.get("id") == document_id:
            chunk_ids.append(ids_list[idx])
    if not chunk_ids:
        raise ValueError(f"No se encontraron chunks asociados al documento con id: {document_id}")
    vectorstore.delete(ids=chunk_ids)
    vectorstore.persist()
    return len(chunk_ids)

def delete_document_by_url(
    url: str,
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data"
) -> int:
    """
    Elimina todos los chunks asociados a una URL (por ejemplo, en el campo 'source_path') en ChromaDB usando LangChain.
    Args:
        url (str): URL o ruta fuente del documento a borrar.
        collection_name (str): Nombre de la colección de ChromaDB.
        persist_dir (str): Directorio de persistencia de ChromaDB.
    Returns:
        int: Número de chunks eliminados.
    Raises:
        ValueError: Si no se encuentran chunks asociados a la URL.
        Exception: Si ocurre un error durante el borrado.
    """
    vectorstore, _ = get_chroma_collection_and_client(collection_name=collection_name, persist_dir=persist_dir)
    all_docs = vectorstore.get(include=["metadatas"])
    chunk_ids = []
    ids_list = all_docs.get("ids", [])
    metadatas_list = all_docs.get("metadatas", [])
    # Buscar coincidencias en todas las tablas/metadatos
    for idx, meta in enumerate(metadatas_list):
        if not meta:
            continue
        # Borrado por coincidencia exacta en 'source_path' o 'url'
        if meta.get("source_path") == url or meta.get("url") == url:
            chunk_ids.append(ids_list[idx])
    if not chunk_ids:
        raise ValueError(f"No se encontraron chunks asociados a la url: {url}")
    vectorstore.delete(ids=chunk_ids)
    vectorstore.persist()
    return len(chunk_ids)

def delete_document_by_source_path(
    source_path: str,
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data"
) -> int:
    """
    Elimina todos los chunks asociados a un source_path en ChromaDB usando LangChain.
    Args:
        source_path (str): Ruta fuente del documento a borrar.
        collection_name (str): Nombre de la colección de ChromaDB.
        persist_dir: str: Directorio de persistencia de ChromaDB.
    Returns:
        int: Número de chunks eliminados.
    Raises:
        ValueError: Si no se encuentran chunks asociados al source_path.
        Exception: Si ocurre un error durante el borrado.
    """
    vectorstore, _ = get_chroma_collection_and_client(collection_name=collection_name, persist_dir=persist_dir)
    all_docs = vectorstore.get(include=["metadatas"])
    chunk_ids = []
    ids_list = all_docs.get("ids", [])
    metadatas_list = all_docs.get("metadatas", [])
    # Buscar coincidencias en todas las tablas/metadatos
    for idx, meta in enumerate(metadatas_list):
        if not meta:
            continue
        if meta.get("source_path") == source_path:
            chunk_ids.append(ids_list[idx])
    if not chunk_ids:
        raise ValueError(f"No se encontraron chunks asociados a source_path: {source_path}")
    vectorstore.delete(ids=chunk_ids)
    vectorstore.persist()
    return len(chunk_ids)

def list_documents(
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data",
    filters: dict = None,
    show_chunks: bool = False
) -> list:
    """
    Lista todos los documentos únicos almacenados en la colección de ChromaDB.
    Agrupa por el campo 'id' y extrae los metadatos principales.
    Permite filtrar por cualquier campo presente en los metadatos.
    Si show_chunks=True, añade el número de chunks asociados a cada documento.

    Args:
        collection_name (str): Nombre de la colección de ChromaDB.
        persist_dir: str: Directorio de persistencia de ChromaDB.
        filters (dict): Diccionario de filtros {campo: valor}.
        show_chunks (bool): Si True, añade el número de chunks por documento.

    Returns:
        list: Lista de diccionarios con los campos ["id", "title", "domain", "date", "chunks"].
    """
    vectorstore, _ = get_chroma_collection_and_client(collection_name=collection_name, persist_dir=persist_dir)
    all_docs = vectorstore.get(include=["metadatas"])
    ids_list = all_docs.get("ids", [])
    metadatas_list = all_docs.get("metadatas", [])
    doc_map = {}
    for idx, meta in enumerate(metadatas_list):
        if not meta:
            continue
        doc_id = meta.get("id")
        if not doc_id:
            continue
        if doc_id not in doc_map:
            doc_map[doc_id] = {
                "id": doc_id,
                "title": meta.get("title") or meta.get("nombre") or "",
                "domain": meta.get("domain", ""),
                "date": meta.get("date") or meta.get("fecha_ingreso") or ""
            }
            if show_chunks:
                doc_map[doc_id]["chunks"] = 1
        else:
            if show_chunks:
                doc_map[doc_id]["chunks"] += 1
    docs = list(doc_map.values())
    # Aplicar filtros si se proporcionan
    if filters:
        def match(doc):
            for k, v in filters.items():
                key = k.lower()
                if key in ("nombre", "title"): key = "title"
                if key in ("dominio", "domain"): key = "domain"
                if key in ("fecha", "date", "fecha_ingreso"): key = "date"
                if str(doc.get(key, "")).lower() != str(v).lower():
                    return False
            return True
        docs = [d for d in docs if match(d)]
    return docs

def count_documents_and_chunks(
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data"
) -> dict:
    """
    Cuenta el número total de documentos únicos y fragmentos (chunks) almacenados en la colección de ChromaDB.

    Args:
        collection_name (str): Nombre de la colección de ChromaDB.
        persist_dir: str: Directorio de persistencia de ChromaDB.

    Returns:
        dict: Diccionario con las claves 'total_documents' y 'total_chunks'.
    """
    vectorstore, _ = get_chroma_collection_and_client(collection_name=collection_name, persist_dir=persist_dir)
    all_docs = vectorstore.get(include=["metadatas"])
    metadatas_list = all_docs.get("metadatas", [])
    total_chunks = len(metadatas_list)
    doc_ids = set()
    for meta in metadatas_list:
        if meta and meta.get("id"):
            doc_ids.add(meta["id"])
    total_documents = len(doc_ids)
    return {"total_documents": total_documents, "total_chunks": total_chunks}

def get_document_with_chunks(
    document_id: str,
    collection_name: str = "meri_chunks",
    persist_dir: str = "chroma_data"
) -> dict | None:
    """
    Recupera los metadatos principales y todos los fragmentos (chunks) asociados a un documento por su ID.
    Args:
        document_id (str): ID del documento.
        collection_name (str): Nombre de la colección de ChromaDB.
        persist_dir (str): Directorio de persistencia de ChromaDB.
    Returns:
        dict: {
            "metadata": metadatos principales del documento,
            "chunks": [ {"id": ..., "chunk_idx": ..., "text": ...}, ... ]
        } o None si no existe.
    """
    vectorstore, _ = get_chroma_collection_and_client(collection_name=collection_name, persist_dir=persist_dir)
    all_docs = vectorstore.get(include=["metadatas", "documents"])
    ids_list = all_docs.get("ids", [])
    metadatas_list = all_docs.get("metadatas", [])
    documents_list = all_docs.get("documents", [])
    # Buscar todos los chunks con ese document_id
    chunks = []
    for idx, meta in enumerate(metadatas_list):
        if meta and meta.get("id") == document_id:
            chunks.append({
                "id": ids_list[idx],
                "chunk_idx": meta.get("chunk_idx", idx),
                "text": documents_list[idx] if idx < len(documents_list) else ""
            })
    if not chunks:
        return None
    # Metadatos principales del primer chunk
    main_meta = {k: v for k, v in metadatas_list[ids_list.index(chunks[0]["id"])].items() if k != "chunk_idx"}
    return {"metadata": main_meta, "chunks": chunks}
