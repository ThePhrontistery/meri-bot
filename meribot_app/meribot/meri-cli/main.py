import click
from typing import Optional

@click.group()
def cli():
    """MeriBot CLI - Herramienta de administración para el chatbot de CECA."""
    pass

@cli.command()
@click.option('--url', help='URL para hacer scraping', required=True)
@click.option('--output', '-o', help='Directorio de salida', default='./data')
def scrape(url: str, output: str):
    """Ejecuta el proceso de scraping en la URL especificada."""
    click.echo(f"Iniciando scraping de {url}...")
    # Implementación del scraping
    click.echo(f"Datos guardados en {output}")

@cli.command()
@click.option('--reset', is_flag=True, help='Reinicia la base de datos')
def db(reset: bool):
    """Gestiona la base de datos vectorial."""
    if reset:
        click.confirm('¿Está seguro que desea reiniciar la base de datos?', abort=True)
        click.echo("Reiniciando base de datos...")
    else:
        click.echo("Estado de la base de datos: OK")

if __name__ == '__main__':
    cli()
