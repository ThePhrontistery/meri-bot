
"""db_commands.py - Subcomandos `db` de la CLI MeriBot: list, delete, show, count."""


import click
import os
import sqlite3

@click.group()
def db():
    """Comandos de administración de la base vectorial (db)"""
    pass

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
