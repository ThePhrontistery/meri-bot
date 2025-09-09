"""
Módulo para ejecución automática semanal del crawler usando APScheduler.
"""

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
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



def run_crawler_job(command=None, workdir=None):
    import subprocess
    import os
    if command:
        print(f"[SCHEDULER] Lanzando job: {command} en {workdir}")
        logging.info(f"[SCHEDULER] Ejecutando comando: {command}")
        try:
            if workdir:
                logging.info(f"[SCHEDULER] Cambiando directorio de trabajo a: {workdir}")
                os.chdir(workdir)
            result = subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[SCHEDULER] Error ejecutando comando: {e}")
            logging.error(f"[SCHEDULER] Error ejecutando comando: {e}")
    else:
        # Fallback: ejecuta el crawler por defecto
        from meribot.crawler.scraper import main as run_scraper
        logging.info("[SCHEDULER] Lanzando job de crawling...")
        run_scraper()
        logging.info("[SCHEDULER] Job de crawling finalizado.")




def schedule_crawler_jobs(scheduler, config):
    """Programa jobs de crawling según la configuración (semanal o puntual)."""
    import os
    scheduler.remove_all_jobs()
    # Tareas puntuales
    if 'tasks' in config:
        for task in config['tasks']:
            if task.get('type') == 'date':
                date_str = task.get('date')
                time_str = task.get('time')
                workdir = task.get('workdir', os.getcwd())
                if date_str and time_str:
                    from datetime import datetime
                    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    print(f"[SCHEDULER] Programando job '{task.get('name', None)}' para {dt} con comando: {task.get('command')} en {workdir}")
                    scheduler.add_job(
                        run_crawler_job,
                        'date',
                        run_date=dt,
                        kwargs={'command': task.get('command'), 'workdir': workdir},
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
    import sys
    import os
    scheduler = BlockingScheduler()
    # Permitir pasar la ruta del YAML como argumento
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = os.path.join(os.getcwd(), 'scheduler_config.yaml')
    print(f"[SCHEDULER] Usando configuración: {config_path}")
    config = load_schedule_config(config_path)
    schedule_crawler_jobs(scheduler, config)
    scheduler.start()
    import time
    print("[SCHEDULER] Scheduler iniciado. Esperando jobs...")
    try:
        while True:
            # Relee la configuración cada 60s y reprograma si hay cambios
            time.sleep(60)
            new_config = load_schedule_config(config_path)
            if new_config != config:
                print("[SCHEDULER] Configuración cambiada. Reprogramando jobs...")
                config = new_config
                schedule_crawler_jobs(scheduler, config)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[SCHEDULER] Scheduler detenido.")

if __name__ == "__main__":
    main()
