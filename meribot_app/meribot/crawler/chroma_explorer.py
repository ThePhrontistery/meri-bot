from langchain_community.vectorstores import Chroma
from langchain_openai import AzureOpenAIEmbeddings
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
import json

console = Console()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header(title: str):
    """Display a styled header."""
    console.print(Panel.fit(
        f"[bold blue]{title}",
        border_style="blue",
        padding=(1, 2)
    ))

def initialize_chroma(persist_dir: str, collection_name: str):
    """Initialize ChromaDB connection."""
    try:
        # Check if required environment variables are set
        required_vars = [
            'AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT',
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_API_VERSION'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            console.print(f"[red]Error: Missing required environment variables: {', '.join(missing_vars)}[/red]")
            console.print("Please set these variables and try again.")
            return None
            
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        db = Chroma(
            persist_directory=persist_dir,
            collection_name=collection_name,
            embedding_function=embeddings
        )
        
        return db
    except Exception as e:
        console.print(f"[red]Error initializing Chroma: {str(e)}[/red]")
        return None

def show_collection_info(db):
    """Display basic collection information."""
    try:
        collection = db._collection
        count = collection.count()
        
        if count == 0:
            console.print("[yellow]The collection is empty.[/yellow]")
            return
            
        # Get a sample document to check embedding dimension
        sample = collection.get(limit=1)
        embed_dim = len(sample['embeddings'][0]) if sample['embeddings'] else "Unknown"
        
        console.print(Panel.fit(
            f"[bold]Collection:[/bold] {db._collection.name}\n"
            f"[bold]Documents:[/bold] {count}\n"
            f"[bold]Embedding Dimension:[/bold] {embed_dim}",
            title="[green]Collection Info[/green]",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[red]Error getting collection info: {str(e)}[/red]")

def search_documents(db, query: str, k: int = 5):
    """Search and display matching documents."""
    try:
        results = db.similarity_search_with_score(query, k=k)
        
        if not results:
            console.print("[yellow]No matching documents found.[/yellow]")
            return
        
        console.print(f"\n[bold]Found {len(results)} results for:[/bold] [cyan]{query}[/cyan]\n")
        
        for i, (doc, score) in enumerate(results, 1):
            content = doc.page_content
            if len(content) > 100:
                content = content[:97] + "..."
                
            console.print(Panel(
                f"[bold]Score:[/bold] {score:.4f}\n"
                f"[bold]Content:[/bold] {content}\n"
                f"[bold]Metadata:[/bold] {json.dumps(doc.metadata, indent=2, ensure_ascii=False)}",
                title=f"Result {i}",
                border_style="blue"
            ))
    except Exception as e:
        console.print(f"[red]Error during search: {str(e)}[/red]")

def main():
    """Main function to run the ChromaDB Explorer."""
    # Default values - user can change these
    PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")
    COLLECTION_NAME = "default"
    
    # Check if persist directory exists
    if not os.path.exists(PERSIST_DIR):
        console.print(f"[yellow]Warning: Directory not found: {PERSIST_DIR}[/yellow]")
        PERSIST_DIR = Prompt.ask("Enter path to Chroma persist directory")
    
    # Initialize Chroma
    db = None
    while db is None:
        db = initialize_chroma(PERSIST_DIR, COLLECTION_NAME)
        if db is None:
            console.print("\n[red]Failed to initialize Chroma.[/red]")
            if not Prompt.ask("Try again?", choices=["y", "n"], default="y") == "y":
                return
    
    # Main menu loop
    while True:
        try:
            clear_screen()
            display_header("ChromaDB Explorer")
            
            console.print("1. View collection info")
            console.print("2. Search documents")
            console.print("3. Change collection")
            console.print("4. Exit")
            
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                show_collection_info(db)
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                query = Prompt.ask("\nEnter search query")
                k = IntPrompt.ask("Number of results", default=5)
                search_documents(db, query, k)
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                new_collection = Prompt.ask("\nEnter new collection name", default=COLLECTION_NAME)
                if new_collection != COLLECTION_NAME:
                    COLLECTION_NAME = new_collection
                    db = initialize_chroma(PERSIST_DIR, COLLECTION_NAME)
                    if db:
                        console.print(f"[green]Switched to collection: {COLLECTION_NAME}[/green]")
                    else:
                        console.print("[red]Failed to switch collections.[/red]")
                    input("\nPress Enter to continue...")
                
            elif choice == "4":
                console.print("\n[green]Goodbye![/green]")
                break
                
        except KeyboardInterrupt:
            console.print("\n[green]Exiting...[/green]")
            break
        except Exception as e:
            console.print(f"\n[red]An error occurred: {str(e)}[/red]")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
