import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

_scheduler = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="America/Mexico_City")
        _scheduler.add_jobstore(DjangoJobStore(), "default")
    return _scheduler


def start_scheduler():
    scheduler = get_scheduler()

    if scheduler.running:
        logger.debug("APScheduler ya está corriendo, se omite re-inicio.")
        return

    # Registrar jobs
    from apps.blog.jobs import publish_scheduled_posts

    scheduler.add_job(
        publish_scheduled_posts,
        trigger="interval",
        minutes=1,
        id="publish_scheduled_posts",
        replace_existing=True,
        misfire_grace_time=30,
        name="Publicar posts programados",
    )

    try:
        scheduler.start()
        logger.info("APScheduler iniciado. Jobs registrados: %s", [j.id for j in scheduler.get_jobs()])
    except Exception as exc:
        logger.error("APScheduler no pudo iniciar: %s", exc)
