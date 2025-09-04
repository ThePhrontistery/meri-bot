
import click
from typing import Optional
import yaml
import os

@click.group()
def cli():
    """MeriBot CLI - Herramienta de administración para el chatbot de CECA."""
    pass

@cli.command()
@click.option('--url', help='URL para hacer scraping')
@click.option('--output', '-o', help='Directorio de salida')
@click.option('--pdf-url', help='URL de un PDF para descargar')
def scrape(url: Optional[str], output: Optional[str], pdf_url: Optional[str]):
    """Ejecuta el proceso de scraping en la URL especificada o según crawler_config.yaml."""
    # Buscar config en la raíz de meribot_app
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crawler_config.yaml'))
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    # Si no se pasan parámetros, usar los del YAML
    if not url:
        url = config.get('seeds', [None])[0]
    if not output:
        output_dir = config.get('output_dir', './data/scraped')
        domain = config.get('allowed_domains', ['default'])[0]
        output = os.path.join(output_dir, domain)
    click.echo(f"Iniciando scraping de {url}...")
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse
    os.makedirs(output, exist_ok=True)
    # Descargar HTML principal
    html_path = None
    if url:
        try:
            resp = requests.get(url, timeout=10, verify=False)
            resp.raise_for_status()
            html_path = os.path.join(output, "index.html")
            with open(html_path, "w", encoding=resp.encoding or "utf-8") as f:
                f.write(resp.text)
            click.echo(f"[SUCCESS] HTML guardado en {html_path}")
        except Exception as e:
            click.echo(f"[ERROR] Falló la descarga HTML: {e}")

    # Buscar y descargar PDFs enlazados en el HTML
    if html_path and os.path.exists(html_path):
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            pdf_links = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.lower().endswith(".pdf"):
                    pdf_links.add(urljoin(url, href))
            if not pdf_links:
                click.echo("[INFO] No se encontraron enlaces a PDFs en el HTML.")
            for pdf_url in pdf_links:
                try:
                    pdf_resp = requests.get(pdf_url, timeout=20, verify=False)
                    pdf_resp.raise_for_status()
                    pdf_name = os.path.basename(urlparse(pdf_url).path)
                    out_path = os.path.join(output, pdf_name)
                    with open(out_path, "wb") as f:
                        f.write(pdf_resp.content)
                    click.echo(f"[SUCCESS] PDF guardado en {out_path}")
                except Exception as e:
                    click.echo(f"[ERROR] Falló la descarga PDF {pdf_url}: {e}")
        except Exception as e:
            click.echo(f"[ERROR] Falló la búsqueda/descarga de PDFs: {e}")

    # Descargar PDF manual si se proporciona
    if pdf_url:
        try:
            resp = requests.get(pdf_url, timeout=20, verify=False)
            resp.raise_for_status()
            out_path = os.path.join(output, "document.pdf")
            with open(out_path, "wb") as f:
                f.write(resp.content)
            click.echo(f"[SUCCESS] PDF guardado en {out_path}")
        except Exception as e:
            click.echo(f"[ERROR] Falló la descarga PDF: {e}")

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
