"""
Módulo para ejecución automática semanal del crawler usando APScheduler.
"""

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
import logging
def load_schedule_config(config_path='scheduler_config.yaml'):
    """
    Carga la configuración de horario desde un archivo YAML.
    Estructura esperada:
    schedule:
      day_of_week: 'sun'
      hour: 2
      minute: 0
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('schedule', {})
    except Exception as e:
        print(f"Error cargando configuración de scheduler: {e}")
        return {}

def run_crawler_job():
    # Importación local para evitar problemas de dependencias circulares
    from meribot.crawler.scraper import main as run_scraper
    logging.info("[SCHEDULER] Lanzando job de crawling...")
    run_scraper()
    logging.info("[SCHEDULER] Job de crawling finalizado.")


def schedule_crawler_job(scheduler, config):
    """Programa el job de crawling usando los parámetros de configuración."""
    scheduler.remove_all_jobs()
    scheduler.add_job(
        run_crawler_job,
        'cron',
        day_of_week=config.get('day_of_week', 'sun'),
        hour=config.get('hour', 2),
        minute=config.get('minute', 0)
    )

def main():
    scheduler = BackgroundScheduler()
    config = load_schedule_config()
    schedule_crawler_job(scheduler, config)
    scheduler.start()
    import time
    print("[SCHEDULER] Scheduler iniciado. Esperando jobs...")
    try:
        while True:
            # Relee la configuración cada 60s y reprograma si hay cambios
            time.sleep(60)
            new_config = load_schedule_config()
            if new_config != config:
                print("[SCHEDULER] Configuración cambiada. Reprogramando job...")
                config = new_config
                schedule_crawler_job(scheduler, config)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[SCHEDULER] Scheduler detenido.")

if __name__ == "__main__":
    main()
