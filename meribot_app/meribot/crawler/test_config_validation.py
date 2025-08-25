
from meribot.crawler.config import load_yaml_config, validate_config, ConfigError
import os

if __name__ == "__main__":
    # Ruta relativa desde la raíz del proyecto
    config_path = os.path.join(os.path.dirname(__file__), "crawler_config.yaml")
    if not os.path.exists(config_path):
        # Intentar ruta relativa desde meribot_app
        config_path = os.path.join(os.path.dirname(__file__), "..", "crawler_config.yaml")
    try:
        config = load_yaml_config(config_path)
        validate_config(config)
        print("¡Configuración válida!")
    except ConfigError as e:
        print(f"Error de configuración: {e}")
    except Exception as ex:
        print(f"Error inesperado: {ex}")
