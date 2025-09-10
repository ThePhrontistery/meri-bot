
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
def list(show_chunks):
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
        if not doc_ids:
            click.echo("No hay documentos embebidos en la base vectorial.")
        else:
            try:
                from tabulate import tabulate
                use_tabulate = True
            except ImportError:
                use_tabulate = False
            headers = ["ID", "Nombre", "Dominio", "Fecha ingreso"]
            rows = []
            campos = ['id', 'title', 'domain', 'date']
            for doc_id in doc_ids:
                valores = {'id': doc_id, 'title': '', 'domain': '', 'date': ''}
                for campo in ['title', 'domain', 'date']:
                    cursor.execute("SELECT string_value FROM embedding_metadata WHERE key = ? AND string_value IS NOT NULL AND id IN (SELECT id FROM embedding_metadata WHERE key = 'id' AND string_value = ?)", (campo, doc_id))
                    resultado = cursor.fetchone()
                    valores[campo] = resultado[0] if resultado else ''
                id_corto = valores['id'][-25:] if valores['id'] else ''
                rows.append([id_corto, valores['title'], valores['domain'], valores['date']])
            if use_tabulate:
                click.echo(tabulate(rows, headers=headers, tablefmt="github"))
            else:
                # Formato manual si no hay tabulate
                click.echo(f"{'ID':25}  {'Nombre':20}  {'Dominio':20}  {'Fecha ingreso':20}")
                click.echo("-"*90)
                for row in rows:
                    click.echo(f"{row[0]:25}  {row[1]:20}  {row[2]:20}  {row[3]:20}")
        conn.close()
    except Exception as e:
        click.echo(f"[ERROR] No se pudo acceder a la base de datos: {e}")
