"""
Script de ejemplo para validar la integración de configuración y logging en el Crawler de Meri-bot.
"""
from .config import get_config, ConfigError
from .logger import get_logger

if __name__ == "__main__":
    logger = get_logger("example")
    logger.info("Iniciando ejemplo de integración de configuración y logging...")
    try:
        config = get_config()
        logger.info("Configuración cargada correctamente.")
        for k, v in config.items():
            logger.debug(f"Config: {k} = {v}")
        logger.info("Simulando operación normal del crawler...")
        logger.warning("Este es un mensaje de advertencia de ejemplo.")
        logger.error("Este es un mensaje de error de ejemplo.")
        logger.critical("Este es un mensaje CRITICAL de ejemplo.")
    except ConfigError as ce:
        logger.error(f"Error de configuración: {ce}")
    except Exception as e:
        logger.exception(f"Excepción inesperada: {e}")
    logger.info("Fin del ejemplo de integración.")
