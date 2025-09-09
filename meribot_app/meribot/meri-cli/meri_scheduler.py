"""
Módulo para ejecución automática semanal del crawler usando APScheduler.
"""

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
import logging
def load_schedule_config(config_path='scheduler_config.yaml'):
    """
    Carga la configuración de horario desde un archivo YAML.
    Soporta dos formatos:
    1. schedule: configuración semanal
    2. tasks: lista de tareas puntuales
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error cargando configuración de scheduler: {e}")
        return {}


def run_crawler_job(command=None):
    import subprocess
    if command:
        logging.info(f"[SCHEDULER] Ejecutando comando: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            logging.info(f"[SCHEDULER] Salida: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logging.error(f"[SCHEDULER] Error ejecutando comando: {e}")
    else:
        # Fallback: ejecuta el crawler por defecto
        from meribot.crawler.scraper import main as run_scraper
        logging.info("[SCHEDULER] Lanzando job de crawling...")
        run_scraper()
        logging.info("[SCHEDULER] Job de crawling finalizado.")



def schedule_crawler_jobs(scheduler, config):
    """Programa jobs de crawling según la configuración (semanal o puntual)."""
    scheduler.remove_all_jobs()
    # Tareas puntuales
    if 'tasks' in config:
        for task in config['tasks']:
            if task.get('type') == 'date':
                date_str = task.get('date')
                time_str = task.get('time')
                if date_str and time_str:
                    from datetime import datetime
                    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    scheduler.add_job(
                        run_crawler_job,
                        'date',
                        run_date=dt,
                        kwargs={'command': task.get('command')},
                        id=task.get('name', None)
                    )
    # Configuración semanal (compatibilidad)
    elif 'schedule' in config:
        scheduler.add_job(
            run_crawler_job,
            'cron',
            day_of_week=config['schedule'].get('day_of_week', 'sun'),
            hour=config['schedule'].get('hour', 2),
            minute=config['schedule'].get('minute', 0)
        )

def main():
    scheduler = BackgroundScheduler()
    config = load_schedule_config()
    schedule_crawler_jobs(scheduler, config)
    scheduler.start()
    import time
    print("[SCHEDULER] Scheduler iniciado. Esperando jobs...")
    try:
        while True:
            # Relee la configuración cada 60s y reprograma si hay cambios
            time.sleep(60)
            new_config = load_schedule_config()
            if new_config != config:
                print("[SCHEDULER] Configuración cambiada. Reprogramando jobs...")
                config = new_config
                schedule_crawler_jobs(scheduler, config)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[SCHEDULER] Scheduler detenido.")

if __name__ == "__main__":
    main()
