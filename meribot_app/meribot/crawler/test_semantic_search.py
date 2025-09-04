#!/usr/bin/env python3
"""
Test de búsqueda semántica en ChromaDB.
Permite buscar en la base de datos por similitud semántica y mostrar los resultados más relevantes.

Uso:
    python -m meribot.crawler.test_semantic_search "texto a buscar"
    python -m meribot.crawler.test_semantic_search "desarrollo profesional" --num_results 10
    python -m meribot.crawler.test_semantic_search "competencias técnicas" -n 5
"""

import argparse
import sys
import os
from typing import List, Dict, Any

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
from dotenv import load_dotenv
import pathlib
ROOT_ENV = pathlib.Path(__file__).resolve().parents[3] / '.env'
load_dotenv(ROOT_ENV)

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from meribot.services.storage.chroma_integration import query_similar_chunks


def format_metadata(metadata: Dict[str, Any]) -> str:
    """
    Formatea los metadatos para mostrar de manera legible.
    """
    if not metadata:
        return "Sin metadatos"
    
    # Campos principales a mostrar
    fields = []
    
    if metadata.get('title'):
        fields.append(f"Título: {metadata['title']}")
    
    if metadata.get('id'):
        fields.append(f"Documento: {metadata['id']}")
    
    if metadata.get('chunk_idx') is not None:
        fields.append(f"Chunk: {metadata['chunk_idx']}")
    
    if metadata.get('type'):
        fields.append(f"Tipo: {metadata['type']}")
    
    if metadata.get('author'):
        fields.append(f"Autor: {metadata['author']}")
    
    if metadata.get('date'):
        date_str = str(metadata['date'])
        if len(date_str) > 20:
            date_str = date_str[:20] + "..."
        fields.append(f"Fecha: {date_str}")
    
    return " | ".join(fields) if fields else "Sin metadatos relevantes"


def display_search_results(results: List[Dict[str, Any]], query: str, num_results: int):
    """
    Muestra los resultados de búsqueda de manera formateada.
    """
    print(f"\n{'='*80}")
    print(f"RESULTADOS DE BÚSQUEDA SEMÁNTICA")
    print(f"{'='*80}")
    print(f"Consulta: '{query}'")
    print(f"Resultados solicitados: {num_results}")
    print(f"Resultados encontrados: {len(results)}")
    print(f"{'='*80}")
    
    if not results:
        print("❌ No se encontraron resultados para la consulta.")
        return
    
    for i, result in enumerate(results, 1):
        score = result.get('score', 0.0)
        document = result.get('document', '')
        metadata = result.get('metadata', {})
        
        # Calcular porcentaje de similitud
        similarity_percent = score * 100 if score <= 1.0 else score
        
        print(f"\n📄 RESULTADO #{i}")
        print(f"{'─'*50}")
        print(f"📊 Similitud: {similarity_percent:.2f}% (score: {score:.4f})")
        print(f"📝 Texto: {document[:200]}{'...' if len(document) > 200 else ''}")
        print(f"🏷️  Metadatos: {format_metadata(metadata)}")
        
        # Si el texto es muy largo, mostrar más información
        if len(document) > 200:
            print(f"📏 Longitud completa: {len(document)} caracteres")


def search_chromadb(query: str, num_results: int = 5, persist_dir: str = "chroma_data") -> List[Dict[str, Any]]:
    """
    Realiza una búsqueda semántica en ChromaDB.
    
    Args:
        query: Texto a buscar
        num_results: Número de resultados a devolver
        persist_dir: Directorio de persistencia de ChromaDB
        
    Returns:
        Lista de resultados con score, document y metadata
    """
    print(f"🔍 Buscando en ChromaDB...")
    print(f"📂 Directorio: {os.path.abspath(persist_dir)}")
    
    # Verificar que existe la base de datos
    chroma_db_path = os.path.join(persist_dir, "chroma.sqlite3")
    if not os.path.exists(chroma_db_path):
        print(f"❌ Error: No se encuentra la base de datos ChromaDB en {chroma_db_path}")
        print(f"💡 Sugerencia: Ejecuta primero el test de procesamiento de documentos:")
        print(f"   python -m meribot.crawler.test_hash_local_docs")
        return []
    
    try:
        results = query_similar_chunks(
            query_text=query,
            n_results=num_results,
            persist_dir=persist_dir,
            collection_name="meri_chunks"
        )
        
        if results is None:
            print("❌ Error: La consulta devolvió None")
            return []
        
        return results
        
    except Exception as e:
        print(f"❌ Error durante la búsqueda: {str(e)}")
        return []


def main():
    """
    Función principal que maneja argumentos de línea de comandos y ejecuta la búsqueda.
    """
    parser = argparse.ArgumentParser(
        description="Búsqueda semántica en ChromaDB",
        epilog="""
Ejemplos de uso:
  python -m meribot.crawler.test_semantic_search "desarrollo profesional"
  python -m meribot.crawler.test_semantic_search "competencias técnicas" -n 10
  python -m meribot.crawler.test_semantic_search "scrum master" --num_results 3
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "query",
        help="Texto a buscar en la base de datos"
    )
    
    parser.add_argument(
        "-n", "--num_results",
        type=int,
        default=5,
        help="Número de resultados a mostrar (por defecto: 5)"
    )
    
    parser.add_argument(
        "--persist_dir",
        default="chroma_data",
        help="Directorio de persistencia de ChromaDB (por defecto: chroma_data)"
    )
    
    parser.add_argument(
        "--collection",
        default="meri_chunks",
        help="Nombre de la colección en ChromaDB (por defecto: meri_chunks)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar información detallada"
    )
    
    args = parser.parse_args()
    
    # Validaciones
    if not args.query.strip():
        print("❌ Error: El texto a buscar no puede estar vacío")
        sys.exit(1)
    
    if args.num_results <= 0:
        print("❌ Error: El número de resultados debe ser mayor que 0")
        sys.exit(1)
    
    if args.verbose:
        print(f"🔧 Configuración:")
        print(f"   Query: '{args.query}'")
        print(f"   Num results: {args.num_results}")
        print(f"   Persist dir: {args.persist_dir}")
        print(f"   Collection: {args.collection}")
    
    # Realizar búsqueda
    try:
        results = search_chromadb(
            query=args.query,
            num_results=args.num_results,
            persist_dir=args.persist_dir
        )
        
        # Mostrar resultados
        display_search_results(results, args.query, args.num_results)
        
        if results:
            print(f"\n✅ Búsqueda completada exitosamente.")
        else:
            print(f"\n⚠️  No se encontraron resultados.")
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Búsqueda interrumpida por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
