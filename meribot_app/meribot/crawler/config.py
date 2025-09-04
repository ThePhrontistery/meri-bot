"""
Módulo de configuración para el Crawler de Meri-bot.
Carga configuración desde YAML, INI y variables de entorno.
Valida campos requeridos y tipos.
Provee acceso centralizado a la configuración.
"""

import os
import yaml
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError

CONFIG_PATH_YAML = os.environ.get("CRAWLER_CONFIG_YAML", os.path.join(os.path.dirname(__file__), "crawler_config.yaml"))


# Esquema formal de configuración usando Pydantic
class CrawlerConfig(BaseModel):
    seeds: List[str] = Field(..., description="Lista de URLs semilla")
    allowed_domains: List[str] = Field(..., description="Dominios permitidos para el crawler")
    user_agent: str = Field(..., description="Agente de usuario HTTP")
    delay: float = Field(..., description="Segundos entre peticiones")
    output_dir: str = Field(..., description="Directorio de salida para los datos extraídos")
    log_level: str = Field(..., description="Nivel de logging (INFO, DEBUG, etc.)")
    chroma_path: str = Field(..., description="Ruta para ChromaDB")
    embedding_model: str = Field(..., description="Modelo de embeddings a usar")
    max_depth: Optional[int] = Field(3, description="Profundidad máxima de crawling")
    file_types: Optional[List[str]] = Field(default_factory=lambda: ["html", "pdf", "docx", "xlsx"], description="Tipos de archivo soportados")

    class Config:
        extra = "forbid"


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
    """
    Valida la configuración usando el esquema formal CrawlerConfig (Pydantic).
    Lanza ConfigError si la validación falla.
    """
    try:
        CrawlerConfig(**config)
    except ValidationError as e:
        raise ConfigError(f"Error de validación en la configuración: {e}")

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
