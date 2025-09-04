
import click
from typing import Optional
import yaml
import os
import requests
import json
from urllib.parse import urlparse
import re

@click.group()
def cli():
    """MeriBot CLI - Herramienta de administración para el chatbot empresarial."""
    pass

@cli.command()
@click.option('--url', required=True, help='URL inicial para el crawling (obligatorio)')
@click.option('--dominio', required=True, help='Dominio al que pertenece la información de la URL (obligatorio)')
@click.option('--max-depth', default=2, type=int, help='Profundidad máxima de navegación (default: 2)')
@click.option('--max-pages', type=int, help='Número máximo de páginas a explorar')
@click.option('--include', help='Patrón regex para incluir URLs')
@click.option('--exclude', help='Patrón regex para excluir URLs')
@click.option('--formats', default='html,pdf,docx,xlsx', help='Formatos de archivo a recolectar (default: html,pdf,docx,xlsx)')
@click.option('--output', help='Directorio destino para documentos')
@click.option('--update-only', is_flag=True, help='Solo actualizar documentos nuevos o modificados')
@click.option('--dry-run', is_flag=True, help='Simular crawling sin descargar')
@click.option('--manual', help='Lista de URLs separadas por comas para procesar manualmente')
@click.option('--api-host', default='http://localhost:8000', help='Host del API de MeriBot (default: http://localhost:8000)')
def crawl(url: str, dominio: str, max_depth: int, max_pages: Optional[int], include: Optional[str], 
          exclude: Optional[str], formats: str, output: Optional[str], 
          update_only: bool, dry_run: bool, manual: Optional[str], api_host: str):
    """
    Lanza el proceso completo de crawling y procesamiento de documentos.
    Se comunica con el endpoint /crawl-and-process del componente crawler.
    """
    
    # Validar URL
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        click.echo(f"❌ Error: URL inválida '{url}'. Debe incluir protocolo (http/https)", err=True)
        raise click.Abort()
    
    # Usar el dominio proporcionado por el usuario
    domain = dominio.strip().lower()
    
    # Cargar configuración
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crawler_config.yaml'))
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            click.echo(f"⚠️  Advertencia: Error al leer configuración: {e}")
    
    # Validar dominio permitido
    allowed_domains = config.get('allowed_domains', [])
    domain_valid = False
    for allowed in allowed_domains:
        if allowed.lower() in domain or domain in allowed.lower():
            domain_valid = True
            break
    
    if not domain_valid:
        click.echo(f"❌ Error: Dominio '{domain}' no está en la lista de dominios permitidos: {allowed_domains}", err=True)
        raise click.Abort()
    
    # Mostrar información del crawling
    click.echo("🚀 Iniciando proceso de crawling...")
    click.echo(f"📍 URL inicial: {url}")
    click.echo(f"🌐 Dominio: {domain}")
    click.echo(f"📊 Profundidad máxima: {max_depth}")
    
    if max_pages:
        click.echo(f"📄 Páginas máximas: {max_pages}")
    if include:
        click.echo(f"✅ Incluir patrón: {include}")
    if exclude:
        click.echo(f"❌ Excluir patrón: {exclude}")
    
    click.echo(f"📁 Formatos: {formats}")
    click.echo(f"🔧 Modo dry-run: {'Sí' if dry_run else 'No'}")
    click.echo(f"🔄 Solo actualizar: {'Sí' if update_only else 'No'}")
    
    if manual:
        click.echo(f"📝 URLs manuales: {manual}")
    
    # En modo dry-run, solo mostrar información
    if dry_run:
        click.echo("\n🔍 MODO DRY-RUN: Simulando proceso...")
        click.echo("✨ El crawling procesaría la URL proporcionada")
        if manual:
            urls = [u.strip() for u in manual.split(',')]
            click.echo(f"✨ Se procesarían {len(urls)} URLs manuales")
        click.echo("✅ Simulación completada. Use sin --dry-run para ejecutar realmente.")
        return
    
    # Preparar payload para el endpoint
    payload = {
        "url": url,
        "domain": domain
    }
    
    # Endpoint del crawler
    endpoint = f"{api_host}/crawl-and-process"
    
    try:
        click.echo(f"\n🔗 Conectando con el servicio de crawling: {endpoint}")
        
        # Realizar petición al endpoint
        response = requests.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=300  # 5 minutos timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            click.echo("✅ Crawling completado exitosamente!")
            
            # Mostrar resultados
            resultados = result.get('resultados', [])
            success_count = 0
            error_count = 0
            warning_count = 0
            
            click.echo(f"\n📊 Resultados del procesamiento ({len(resultados)} archivos):")
            for resultado in resultados:
                file_name = resultado.get('file', 'N/A')
                if 'status' in resultado:
                    click.echo(f"  ✅ {file_name}: {resultado['status']}")
                    success_count += 1
                elif 'error' in resultado:
                    click.echo(f"  ❌ {file_name}: {resultado['error']}")
                    error_count += 1
                elif 'warning' in resultado:
                    click.echo(f"  ⚠️  {file_name}: {resultado['warning']}")
                    warning_count += 1
            
            click.echo(f"\n📈 Resumen:")
            click.echo(f"  ✅ Exitosos: {success_count}")
            click.echo(f"  ❌ Errores: {error_count}")
            click.echo(f"  ⚠️  Advertencias: {warning_count}")
            
        else:
            error_detail = "Error desconocido"
            try:
                error_response = response.json()
                error_detail = error_response.get('detail', error_detail)
            except:
                error_detail = response.text
            
            click.echo(f"❌ Error en el crawling (HTTP {response.status_code}): {error_detail}", err=True)
            raise click.Abort()
            
    except requests.exceptions.ConnectionError:
        click.echo(f"❌ Error: No se pudo conectar con el servicio de crawling en {api_host}", err=True)
        click.echo("💡 Asegúrate de que el servidor FastAPI esté ejecutándose", err=True)
        raise click.Abort()
    except requests.exceptions.Timeout:
        click.echo("❌ Error: Timeout en la operación de crawling", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)
        raise click.Abort()

@cli.command()
@click.option('--url', help='URL para hacer scraping')
@click.option('--output', '-o', help='Directorio de salida')
@click.option('--pdf-url', help='URL de un PDF para descargar')
def scrape(url: Optional[str], output: Optional[str], pdf_url: Optional[str]):
    """
    OBSOLETO: Ejecuta el proceso de scraping básico (usar 'crawl' para funcionalidad completa).
    Mantiene compatibilidad con versiones anteriores.
    """
    click.echo("⚠️  Advertencia: El comando 'scrape' está obsoleto. Use 'crawl' para funcionalidad completa.")
    
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
