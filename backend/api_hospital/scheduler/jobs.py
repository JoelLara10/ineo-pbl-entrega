import atexit

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = None
flask_app = None


def _automatic_backup():
    from utils.backups import (
        cargar_config_automatizacion,
        limpiar_backups,
        realizar_backup,
    )

    config = cargar_config_automatizacion()
    if not config.get('activo') or flask_app is None:
        return

    with flask_app.app_context():
        realizar_backup(
            tipo=config.get('tipo', 'completa'),
            formato=config.get('formato', 'json'),
            colecciones=config.get('colecciones') or None,
            es_automatico=True,
        )
        limpiar_backups(config.get('max_backups', 4))


def configure_backup_job(config):
    if scheduler is None:
        return

    if scheduler.get_job('backup_automatico'):
        scheduler.remove_job('backup_automatico')

    if config.get('activo'):
        scheduler.add_job(
            _automatic_backup,
            'interval',
            minutes=int(config.get('intervalo', 1440)),
            id='backup_automatico',
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )


def init_scheduler(app):
    global scheduler, flask_app
    if scheduler is not None:
        return scheduler

    flask_app = app
    scheduler = BackgroundScheduler()
    scheduler.start()

    from utils.backups import cargar_config_automatizacion
    configure_backup_job(cargar_config_automatizacion())

    atexit.register(lambda: scheduler.shutdown(wait=False) if scheduler.running else None)
    return scheduler


def get_scheduler():
    return scheduler
