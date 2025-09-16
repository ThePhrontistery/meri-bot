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
    if (spec is None):
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
@click.option('--id', 'document_id', required=False, help="ID del documento a borrar. Es el identificador único asignado al documento en la base vectorial.")
@click.option('--url', 'document_url', required=False, help="URL o ruta fuente del documento a borrar. Borra todos los chunks asociados a esa URL.")
@click.option('--source-path', 'document_source_path', required=False, help="source_path del documento a borrar. Borra todos los chunks asociados a ese source_path.")
def delete(document_id, document_url, document_source_path):
    """
    Elimina un documento y todos sus chunks asociados usando el endpoint del crawler.
    Permite borrar por ID, por URL o por source_path.
    """
    import click
    import os
    import requests
    # Validación de exclusividad
    options = [bool(document_id), bool(document_url), bool(document_source_path)]
    if sum(options) == 0:
        click.echo("[ERROR] Debe especificar --id, --url o --source-path para borrar un documento.")
        return
    if sum(options) > 1:
        click.echo("[ERROR] No puede usar más de una opción (--id, --url, --source-path) al mismo tiempo. Elija solo una.")
        return
    CRAWLER_URL = os.getenv("MERIBOT_CRAWLER_URL", "http://localhost:8000")
    if document_id:
        endpoint = f"{CRAWLER_URL}/delete-document"
        try:
            response = requests.delete(endpoint, params={"id": document_id}, timeout=30)
            if response.status_code == 200:
                click.echo(f"[SUCCESS] Documento y chunks asociados eliminados correctamente (id: {document_id})")
            else:
                click.echo(f"[ERROR] Falló el borrado: {response.status_code} {response.text}")
        except Exception as e:
            click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")
    elif document_url:
        endpoint = f"{CRAWLER_URL}/delete-document-by-url"
        try:
            response = requests.delete(endpoint, params={"url": document_url}, timeout=30)
            if response.status_code == 200:
                click.echo(f"[SUCCESS] Chunks asociados a la URL eliminados correctamente (url: {document_url})")
            else:
                click.echo(f"[ERROR] Falló el borrado por URL: {response.status_code} {response.text}")
        except Exception as e:
            click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")
    elif document_source_path:
        endpoint = f"{CRAWLER_URL}/delete-document-by-source-path"
        try:
            response = requests.delete(endpoint, params={"source_path": document_source_path}, timeout=30)
            if response.status_code == 200:
                click.echo(f"[SUCCESS] Chunks asociados al source_path eliminados correctamente (source_path: {document_source_path})")
            else:
                click.echo(f"[ERROR] Falló el borrado por source_path: {response.status_code} {response.text}")
        except Exception as e:
            click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")


@db.command()
@click.option('--id', 'document_id', required=True, help="ID del documento a mostrar. Es el identificador único asignado al documento en la base vectorial.")
def show(document_id):
    """
    Muestra los metadatos y detalles de un documento almacenado en la base vectorial (Chroma DB).
    """
    import requests
    import click
    import os
    try:
        CRAWLER_URL = os.getenv("MERIBOT_CRAWLER_URL", "http://localhost:8000")
        endpoint = f"{CRAWLER_URL}/show-document"
        response = requests.get(endpoint, params={"id": document_id}, timeout=30)
        if response.status_code == 404:
            click.echo(f"[ERROR] No existe un documento con id: {document_id}")
            return
        if response.status_code != 200:
            click.echo(f"[ERROR] Falló la consulta: {response.status_code} {response.text}")
            return
        data = response.json()
        metadatos = data.get("metadata", {})
        chunks = data.get("chunks", [])
        # Mostrar metadatos en formato tabla si tabulate está disponible
        try:
            from tabulate import tabulate
            use_tabulate = True
        except ImportError:
            use_tabulate = False
        # Limitar la columna Valor a 40 caracteres y preparar para tabla horizontal
        metadatos_dict = {}
        for k, v in sorted(metadatos.items()):
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
        if chunks:
            chunk_rows = []
            for idx, chunk in enumerate(chunks):
                # Word wrap manual a 50 caracteres
                def wrap_text(text, width=50):
                    if not text:
                        return ''
                    import textwrap
                    return '\n'.join(textwrap.wrap(text, width=width))
                chunk_rows.append({
                    "Chunk #": idx,
                    "id": chunk.get("id", ""),
                    "text": wrap_text(chunk.get("text", ""), 50)
                })
            if use_tabulate:
                table = tabulate(chunk_rows, headers="keys", tablefmt="grid", stralign="left", disable_numparse=True)
                click.echo(f"\nChunks asociados:\n" + table)
            else:
                click.echo(f"\nChunks asociados:")
                for row in chunk_rows:
                    click.echo(f"Chunk {row['Chunk #']}: id={row['id']}\n{row['text']}\n")
        else:
            click.echo("[INFO] No hay fragmentos asociados a este documento.")
    except Exception as e:
        click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")


@db.command()
@click.option('--filter', 'filter_', default=None, help="Filtra la lista de documentos por <campo>:<valor> (ej: dominio:cca)")
@click.option('--show-chunks', is_flag=True, help="Muestra también el número de fragmentos (chunks) asociados a cada documento.")
def list(filter_, show_chunks):
    """
    Lista todos los documentos almacenados en la base vectorial a través del endpoint del crawler.
    Muestra las columnas: ["ID", "Nombre", "Dominio", "Fecha ingreso"].
    Permite filtrar por campo usando --filter <campo>:<valor>.
    Si se pasa --show-chunks, muestra también el número de fragmentos asociados a cada documento.
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
        if show_chunks:
            params['show_chunks'] = 'true'
        response = requests.get(endpoint, params=params, timeout=30)
        if response.status_code == 200:
            docs = response.json().get("documents", [])
            if not docs:
                click.echo("No hay documentos almacenados en la base vectorial.")
                return
            headers = ["ID", "Nombre", "Dominio", "Fecha ingreso"]
            if show_chunks:
                headers.append("Chunks")
            try:
                from tabulate import tabulate
                table = tabulate(
                    [
                        [d.get("id", ""), d.get("title", ""), d.get("domain", ""), d.get("date", "")] + ([d.get("chunks", "")] if show_chunks else [])
                        for d in docs
                    ],
                    headers=headers,
                    tablefmt="github"
                )
                click.echo(table)
            except ImportError:
                click.echo("\t".join(headers))
                for d in docs:
                    row = [d.get('id',''), d.get('title',''), d.get('domain',''), d.get('date','')]
                    if show_chunks:
                        row.append(str(d.get('chunks','')))
                    click.echo("\t".join(row))
        else:
            click.echo(f"[ERROR] Falló la consulta: {response.status_code} {response.text}")
    except Exception as e:
        click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")


@db.command()
def count():
    """
    Muestra el número total de documentos únicos y fragmentos (chunks) almacenados en la base vectorial.
    """
    import requests
    import click
    import os
    try:
        CRAWLER_URL = os.getenv("MERIBOT_CRAWLER_URL", "http://localhost:8000")
        endpoint = f"{CRAWLER_URL}/count-documents"
        response = requests.get(endpoint, timeout=30)
        if response.status_code == 200:
            data = response.json()
            total_docs = data.get("total_documents", 0)
            total_chunks = data.get("total_chunks", 0)
            click.echo(f"Total de documentos únicos: {total_docs}")
            click.echo(f"Total de fragmentos (chunks): {total_chunks}")
        else:
            click.echo(f"[ERROR] Falló la consulta: {response.status_code} {response.text}")
    except Exception as e:
        click.echo(f"[ERROR] No se pudo conectar al endpoint del crawler: {e}")
