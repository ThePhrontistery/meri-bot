"""
Módulo de configuración para el Crawler de Meri-bot.
Carga configuración desde YAML, INI y variables de entorno.
Valida campos requeridos y tipos.
Provee acceso centralizado a la configuración.
"""
import os
import yaml
from typing import Any, Dict

CONFIG_PATH_YAML = os.environ.get("CRAWLER_CONFIG_YAML", os.path.join(os.path.dirname(__file__), "crawler_config.yaml"))

REQUIRED_FIELDS = [
    "seeds",
    "allowed_domains",
    "user_agent",
    "delay",
    "output_dir",
    "log_level",
    "chroma_path",
    "embedding_model"
]

class ConfigError(Exception):
    pass

def load_yaml_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def override_with_env(config: Dict[str, Any]) -> Dict[str, Any]:
    # Permite override de campos por variables de entorno
    for key in config:
        env_key = f"CRAWLER_{key.upper()}"
        if env_key in os.environ:
            value = os.environ[env_key]
            # Convertir tipos básicos
            if isinstance(config[key], float):
                value = float(value)
            elif isinstance(config[key], int):
                value = int(value)
            elif isinstance(config[key], list):
                value = value.split(",")
            config[key] = value
    return config

def validate_config(config: Dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in config or config[f] is None]
    if missing:
        raise ConfigError(f"Faltan campos requeridos en la configuración: {missing}")
    # Validaciones básicas de tipo
    if not isinstance(config["seeds"], list):
        raise ConfigError("El campo 'seeds' debe ser una lista de URLs")
    if not isinstance(config["allowed_domains"], list):
        raise ConfigError("El campo 'allowed_domains' debe ser una lista")
    if not isinstance(config["delay"], (float, int)):
        raise ConfigError("El campo 'delay' debe ser numérico (float o int)")
    if not isinstance(config["output_dir"], str):
        raise ConfigError("El campo 'output_dir' debe ser string")
    if not isinstance(config["log_level"], str):
        raise ConfigError("El campo 'log_level' debe ser string")
    if not isinstance(config["chroma_path"], str):
        raise ConfigError("El campo 'chroma_path' debe ser string")
    if not isinstance(config["embedding_model"], str):
        raise ConfigError("El campo 'embedding_model' debe ser string")

def get_config() -> Dict[str, Any]:
    """Carga y valida la configuración global del crawler."""
    config = load_yaml_config(CONFIG_PATH_YAML)
    config = override_with_env(config)
    validate_config(config)
    return config

if __name__ == "__main__":
    import sys
    try:
        config = get_config()
        print("\nConfiguración cargada correctamente:\n")
        for k, v in config.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
