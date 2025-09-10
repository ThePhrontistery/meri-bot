import yaml

def load_config_from_yaml(param: str):
    """
    Carga el valor de un parámetro específico desde crawler_config.yaml.
    Devuelve el valor del parámetro o None si no existe o hay error.
    """
    CRAWLER_CONFIG_PATH = os.path.abspath(os.getenv('CRAWLER_CONFIG_PATH', 'crawler_config.yaml'))
    if not os.path.exists(CRAWLER_CONFIG_PATH):
        return None
    try:
        with open(CRAWLER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        value = config.get(param, None)
        return value
    except Exception:
        return None
"""
utils.py
Funciones utilitarias generales para MeriBot.
"""


import os

def load_system_prompt():
    """
    Carga el prompt de sistema desde la ruta especificada en la variable de entorno SYSTEM_PROMPT_PATH.
    """
    system_prompt_path = os.getenv('SYSTEM_PROMPT_PATH')
    with open(system_prompt_path, 'r', encoding='utf-8') as f:
        return f.read()
