import click
import os
import sqlite3
import requests
# Cargar variables de entorno desde .env automáticamente
from dotenv import load_dotenv
load_dotenv()

# Importar VectorSearch para acceso a Chroma (robusto a cualquier modo de ejecución)
try:
    from meribot.core.vector_search import VectorSearch
except ModuleNotFoundError:
    import importlib.util
    import sys, os
    core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../core'))
    sys.path.append(core_path)
    spec = importlib.util.find_spec("vector_search")
    if spec is None:
        raise ImportError("No se pudo encontrar vector_search.py en ../core/")
    vector_search = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vector_search)
    VectorSearch = vector_search.VectorSearch


# Un solo grupo db para todos los subcomandos
@click.group()
def db():
    """Comandos de administración de la base vectorial (db)"""
    pass


# Comando para borrar un documento y sus chunks de Chroma
@db.command()
@click.option('--id', 'document_id', required=True, help="ID del documento a borrar. Es el identificador único asignado al documento en la base vectorial.")
def delete(document_id):
    """
    Elimina un documento y todos sus chunks asociados usando el endpoint del crawler.
    Realiza una petición HTTP DELETE a /delete-document.
    """
    import click
    import os
    # URL base del crawler (ajustar si es necesario)
    CRAWLER_URL = os.getenv("MERIBOT_CRAWLER_URL", "http://localhost:8000")
    endpoint = f"{CRAWLER_URL}/delete-document"
    try:
        response = requests.delete(endpoint, params={"id": document_id}, timeout=30)
        if response.status_code == 200:
            click.echo(f"[SUCCESS] Documento y chunks asociados eliminados correctamente (id: {document_id})")
        else:
            click.echo(f"[ERROR] Falló el borrado: {response.status_code} {response.text}")
    except Exception as e:
        click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")


@db.command()
@click.option('--id', 'document_id', required=True, help="ID del documento a mostrar. Es el identificador único asignado al documento en la base vectorial.")
def show(document_id):
    """
    Muestra los metadatos y detalles de un documento almacenado en la base vectorial (Chroma DB).
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chroma_data'))
    db_path = os.path.join(base_dir, 'chroma.sqlite3')
    if not os.path.exists(db_path):
        click.echo(f"[ERROR] No se encontró la base de datos: {db_path}")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Buscar si existe el documento
        cursor.execute("SELECT 1 FROM embedding_metadata WHERE key = 'id' AND string_value = ?", (document_id,))
        if not cursor.fetchone():
            click.echo(f"[ERROR] No existe un documento con id: {document_id}")
            conn.close()
            return
        # Obtener todos los metadatos únicos para ese documento
        cursor.execute("SELECT key, string_value FROM embedding_metadata WHERE id IN (SELECT id FROM embedding_metadata WHERE key = 'id' AND string_value = ?) AND string_value IS NOT NULL", (document_id,))
        metadatos = cursor.fetchall()
        if not metadatos:
            click.echo(f"[ERROR] No se encontraron metadatos para el documento: {document_id}")
            conn.close()
            return
        # Mostrar metadatos en formato tabla si tabulate está disponible
        try:
            from tabulate import tabulate
            use_tabulate = True
        except ImportError:
            use_tabulate = False


        # Limitar la columna Valor a 40 caracteres y preparar para tabla horizontal
        metadatos_dict = {}
        for k, v in sorted(metadatos):
            if k == 'chroma:document':
                continue  # Omitir esta columna
            if v and len(str(v)) > 40:
                metadatos_dict[k] = str(v)[:37] + '...'
            else:
                metadatos_dict[k] = v


        if use_tabulate:
            table = tabulate([metadatos_dict], headers="keys", tablefmt="github")
            click.echo(f"\nDetalles del documento: {document_id}\n" + table)
        else:
            click.echo(f"\nDetalles del documento: {document_id}\n" + "-"*40)
            for k in metadatos_dict:
                click.echo(f"{k:15}: {metadatos_dict[k]}")

        # Mostrar tabla de chunks asociados
        cursor.execute("SELECT id FROM embedding_metadata WHERE key = 'id' AND string_value = ?", (document_id,))
        chunk_ids = [row[0] for row in cursor.fetchall()]
        if chunk_ids:
            chunk_rows = []
            for idx, chunk_row_id in enumerate(chunk_ids):
                # Buscar texto del chunk si está disponible
                cursor.execute("SELECT string_value FROM embedding_metadata WHERE key = 'text' AND id = ?", (chunk_row_id,))
                chunk_text = cursor.fetchone()
                if chunk_text and chunk_text[0]:
                    texto_completo = chunk_text[0]
                else:
                    # Si no hay texto, buscar en chroma:document
                    cursor.execute("SELECT string_value FROM embedding_metadata WHERE key = 'chroma:document' AND id = ?", (chunk_row_id,))
                    doc_text = cursor.fetchone()
                    if doc_text and doc_text[0]:
                        texto_completo = doc_text[0]
                    else:
                        texto_completo = ''
                # Word wrap manual a 50 caracteres
                def wrap_text(text, width=50):
                    if not text:
                        return ''
                    import textwrap
                    return '\n'.join(textwrap.wrap(text, width=width))

                chunk_rows.append({
                    "Chunk #": idx,
                    "id": chunk_row_id,
                    "text": wrap_text(texto_completo, 50)
                })
            if use_tabulate:
                # Usar tablefmt='grid' para que el alto de la fila se ajuste al texto multilinea
                table = tabulate(chunk_rows, headers="keys", tablefmt="grid", stralign="left", disable_numparse=True)
                click.echo(f"\nChunks asociados:\n" + table)
            else:
                click.echo(f"\nChunks asociados:")
                for row in chunk_rows:
                    click.echo(f"Chunk {row['Chunk #']}: id={row['id']}\n{row['text']}\n")
        conn.close()
    except Exception as e:
        click.echo(f"[ERROR] No se pudo acceder a la base de datos: {e}")


@db.command()
@click.option('--filter', 'filter_', default=None, help="Filtra la lista de documentos por <campo>:<valor> (ej: dominio:cca)")
def list(filter_):
    """
    Lista todos los documentos almacenados en la base vectorial a través del endpoint del crawler.
    Muestra las columnas: ["ID", "Nombre", "Dominio", "Fecha ingreso"].
    Permite filtrar por campo usando --filter <campo>:<valor>.
    """
    import requests
    import click
    import os
    try:
        CRAWLER_URL = os.getenv("MERIBOT_CRAWLER_URL", "http://localhost:8000")
        endpoint = f"{CRAWLER_URL}/list-documents"
        params = {}
        if filter_:
            if ':' not in filter_:
                click.echo("[ERROR] El filtro debe tener el formato <campo>:<valor> (ej: dominio:cca)")
                return
            campo, valor = filter_.split(':', 1)
            params[campo] = valor
        response = requests.get(endpoint, params=params, timeout=30)
        if response.status_code == 200:
            docs = response.json().get("documents", [])
            if not docs:
                click.echo("No hay documentos almacenados en la base vectorial.")
                return
            headers = ["ID", "Nombre", "Dominio", "Fecha ingreso"]
            try:
                from tabulate import tabulate
                table = tabulate(
                    [[d.get("id", ""), d.get("title", ""), d.get("domain", ""), d.get("date", "") ] for d in docs],
                    headers=headers,
                    tablefmt="github"
                )
                click.echo(table)
            except ImportError:
                click.echo("\t".join(headers))
                for d in docs:
                    click.echo(f"{d.get('id','')}\t{d.get('title','')}\t{d.get('domain','')}\t{d.get('date','')}")
        else:
            click.echo(f"[ERROR] Falló la consulta: {response.status_code} {response.text}")
    except Exception as e:
        click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")
