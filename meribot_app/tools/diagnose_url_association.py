import os

# Cambia este path si tu scraping guarda en otro directorio
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/scraped/cca.capgemini.com'))

for root, dirs, files in os.walk(DOCS_DIR):
    for fname in files:
        if fname.endswith('.pdf') or fname.endswith('.docx') or fname.endswith('.xlsx') or fname.endswith('.html'):
            doc_path = os.path.join(root, fname)
            url_path = doc_path + '.url'
            print(f'\nDocumento: {doc_path}')
            if os.path.exists(url_path):
                with open(url_path, 'r', encoding='utf-8') as f:
                    url = f.read().strip()
                print(f'  URL asociada (.url): {url}')
            else:
                print('  [!] No existe archivo .url asociado')
