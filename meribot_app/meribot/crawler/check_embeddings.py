#!/usr/bin/env python3
"""
CLI/REPL de búsqueda semántica con LangChain + Chroma + Azure OpenAI
"""

import os
import argparse
import sys
from typing import List, Tuple, Optional
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain.schema import Document

# Load environment variables from .env file if it exists
load_dotenv()

class SemanticSearchCLI:
    def __init__(self):
        self.parser = self._create_parser()
        self.args = None
        self.embeddings = None
        self.vectorstore = None

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description='Búsqueda semántica con LangChain + Chroma + Azure OpenAI',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        
        # Required arguments
        parser.add_argument(
            '--persist',
            required=True,
            help='Ruta del directorio de persistencia de Chroma',
        )
        
        # Optional arguments
        parser.add_argument(
            '--collection',
            default='default',
            help='Nombre de la colección',
        )
        
        parser.add_argument(
            '--k',
            type=int,
            default=5,
            help='Número de resultados a devolver',
        )
        
        parser.add_argument(
            '--q',
            help='Consulta directa (opcional, si no se proporciona se inicia el modo REPL)',
        )
        
        parser.add_argument(
            '--azure-deployment',
            default=os.getenv('AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT'),
            help='Nombre del deployment de embeddings de Azure',
        )
        
        return parser

    def _validate_environment(self) -> bool:
        """Validate required environment variables and arguments."""
        required_vars = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_API_VERSION',
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"Error: Faltan variables de entorno requeridas: {', '.join(missing_vars)}", file=sys.stderr)
            return False
            
        if not self.args.azure_deployment:
            print("Error: Se requiere --azure-deployment o la variable de entorno AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", 
                  file=sys.stderr)
            return False
            
        if not os.path.exists(self.args.persist):
            print(f"Error: El directorio de persistencia no existe: {self.args.persist}", file=sys.stderr)
            return False
            
        return True
    
    def _initialize_embeddings(self) -> bool:
        """Initialize Azure OpenAI embeddings client."""
        try:
            self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=self.args.azure_deployment,
                openai_api_type="azure",
                openai_api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                openai_api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            )
            return True
        except Exception as e:
            print(f"Error al inicializar los embeddings: {str(e)}", file=sys.stderr)
            return False
    
    def _initialize_vectorstore(self) -> bool:
        """Initialize Chroma vector store."""
        try:
            self.vectorstore = Chroma(
                persist_directory=self.args.persist,
                collection_name=self.args.collection,
                embedding_function=self.embeddings
            )
            return True
        except Exception as e:
            print(f"Error al inicializar Chroma: {str(e)}", file=sys.stderr)
            return False
    
    def _format_result(self, doc: Document, score: float, rank: int) -> str:
        """Format a single search result."""
        doc_id = doc.metadata.get('id') or doc.metadata.get('source') or "(sin id)"
        # Truncate the text to ~140 characters
        text = doc.page_content
        if len(text) > 140:
            text = text[:137] + "..."
        
        return f"[{rank}] dist={score:.4f} id={doc_id}  texto: {text}"
    
    def search(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        if not query.strip():
            return []
            
        try:
            return self.vectorstore.similarity_search_with_score(query, k=k)
        except Exception as e:
            print(f"Error en la búsqueda: {str(e)}", file=sys.stderr)
            return []
    
    def print_results(self, results: List[Tuple[Document, float]]) -> None:
        """Print search results."""
        if not results:
            print("Sin resultados.")
            return
            
        for i, (doc, score) in enumerate(results, 1):
            print(self._format_result(doc, score, i))
    
    def run_repl(self) -> None:
        """Run the REPL interface."""
        print("REPL de búsqueda por similitud. Escribe tu consulta o 'salir'.")
        
        while True:
            try:
                query = input("> ").strip()
                
                if query.lower() in ('salir', 'exit', 'quit'):
                    print("Fin.")
                    break
                    
                if not query:
                    continue
                    
                results = self.search(query, self.args.k)
                self.print_results(results)
                
            except (KeyboardInterrupt, EOFError):
                print("\nSaliendo...")
                break
            except Exception as e:
                print(f"Error: {str(e)}", file=sys.stderr)
    
    def run(self) -> int:
        """Run the CLI application."""
        self.args = self.parser.parse_args()
        
        if not self._validate_environment():
            return 1
            
        if not self._initialize_embeddings():
            return 1
            
        if not self._initialize_vectorstore():
            return 1
        
        # Single query mode
        if self.args.q:
            results = self.search(self.args.q, self.args.k)
            self.print_results(results)
        # REPL mode
        else:
            self.run_repl()
            
        return 0


def main() -> int:
    """Main entry point."""
    cli = SemanticSearchCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
