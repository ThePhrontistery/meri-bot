import click
import os
import sqlite3
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
    Elimina un documento y todos sus fragmentos (chunks) y datos asociados de las tablas embedding* de la base vectorial (Chroma DB).
    """
    import os
    import sqlite3
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chroma_data'))
    db_path = os.path.join(base_dir, 'chroma.sqlite3')
    if not os.path.exists(db_path):
        click.echo(f"[ERROR] No se encontró la base de datos: {db_path}")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Buscar todos los ids de fragmentos asociados al documento
        cursor.execute("SELECT id FROM embedding_metadata WHERE key = 'id' AND string_value = ?", (document_id,))
        chunk_ids = [row[0] for row in cursor.fetchall()]
        if not chunk_ids:
            click.echo(f"[ERROR] No se encontraron fragmentos asociados al documento con id: {document_id}")
            conn.close()
            return
        # Eliminar de embedding_metadata
        cursor.executemany("DELETE FROM embedding_metadata WHERE id = ?", [(cid,) for cid in chunk_ids])
        # Eliminar de embeddings
        cursor.executemany("DELETE FROM embeddings WHERE segment_id = ?", [(cid,) for cid in chunk_ids])
        # Eliminar de otras tablas embedding* si existen (opcional, seguro)
        # Puedes añadir más sentencias DELETE aquí si hay más tablas relacionadas
        conn.commit()
        click.echo(f"Se eliminaron {len(chunk_ids)} fragmentos y sus datos asociados del documento con id: {document_id}.")
        conn.close()
    except Exception as e:
        click.echo(f"[ERROR] No se pudo eliminar el documento: {e}")

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
@click.option('--show-chunks', is_flag=True, help="Mostrar chunks asociados si están disponibles")
@click.option('--filter', '-f', multiple=True, help="Filtra la lista de documentos por <campo>:<valor>. Puede usarse varias veces.")
def list(show_chunks, filter):
    """
    Lista documentos almacenados en la base vectorial (Chroma DB).
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chroma_data'))
    db_path = os.path.join(base_dir, 'chroma.sqlite3')
    if not os.path.exists(db_path):
        click.echo(f"[ERROR] No se encontró la base de datos: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Paso 3: Listar documentos embebidos únicos usando embedding_metadata
        cursor.execute("SELECT DISTINCT string_value FROM embedding_metadata WHERE key = ? AND string_value IS NOT NULL", ('id',))
        doc_ids = [row[0] for row in cursor.fetchall()]
        # Aplicar filtros generales --filter campo:valor
        if filter:
            filtered_doc_ids = []
            for doc_id in doc_ids:
                match = True
                for filtro in filter:
                    if ':' not in filtro:
                        click.echo(f"[ERROR] Filtro mal formado: '{filtro}'. Usa --filter campo:valor")
                        return
                    campo, valor = filtro.split(':', 1)
                    cursor.execute("SELECT 1 FROM embedding_metadata WHERE key = ? AND string_value = ? AND id IN (SELECT id FROM embedding_metadata WHERE key = 'id' AND string_value = ?)", (campo, valor, doc_id))
                    if not cursor.fetchone():
                        match = False
                        break
                if match:
                    filtered_doc_ids.append(doc_id)
            doc_ids = filtered_doc_ids
        if not doc_ids:
            click.echo("No hay documentos embebidos en la base vectorial.")
        else:
            try:
                from tabulate import tabulate
                use_tabulate = True
            except ImportError:
                use_tabulate = False
            if show_chunks:
                headers = ["ID", "Nombre", "Dominio", "Fecha ingreso", "# Chunks"]
            else:
                headers = ["ID", "Nombre", "Dominio", "Fecha ingreso"]
            rows = []
            campos = ['id', 'title', 'domain', 'date']
            for doc_id in doc_ids:
                valores = {'id': doc_id, 'title': '', 'domain': '', 'date': ''}
                for campo in ['title', 'domain', 'date']:
                    cursor.execute("SELECT string_value FROM embedding_metadata WHERE key = ? AND string_value IS NOT NULL AND id IN (SELECT id FROM embedding_metadata WHERE key = 'id' AND string_value = ?)", (campo, doc_id))
                    resultado = cursor.fetchone()
                    valores[campo] = resultado[0] if resultado else ''
                id_completo = valores['id'] if valores['id'] else ''
                if show_chunks:
                    cursor.execute("SELECT COUNT(*) FROM embedding_metadata WHERE key = 'id' AND string_value = ?", (doc_id,))
                    num_chunks = cursor.fetchone()[0]
                    rows.append([id_completo, valores['title'], valores['domain'], valores['date'], num_chunks])
                else:
                    rows.append([id_completo, valores['title'], valores['domain'], valores['date']])
            if use_tabulate:
                click.echo(tabulate(rows, headers=headers, tablefmt="github"))
            else:
                if show_chunks:
                    click.echo(f"{'ID':25}  {'Nombre':20}  {'Dominio':20}  {'Fecha ingreso':20}  {'# Chunks':8}")
                    click.echo("-"*100)
                    for row in rows:
                        click.echo(f"{row[0]:25}  {row[1]:20}  {row[2]:20}  {row[3]:20}  {row[4]:8}")
                else:
                    click.echo(f"{'ID':25}  {'Nombre':20}  {'Dominio':20}  {'Fecha ingreso':20}")
                    click.echo("-"*90)
                    for row in rows:
                        click.echo(f"{row[0]:25}  {row[1]:20}  {row[2]:20}  {row[3]:20}")
        conn.close()
    except Exception as e:
        click.echo(f"[ERROR] No se pudo acceder a la base de datos: {e}")
