import os
import sys
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

_SKIP_COMMANDS = {
    "migrate", "makemigrations", "collectstatic", "createsuperuser",
    "createcachetable", "test", "check", "inspectdb", "dumpdata",
    "loaddata", "flush", "dbshell", "showmigrations", "sqlmigrate",
}


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        # Bloquear comandos de gestión que no deben iniciar el scheduler
        if len(sys.argv) > 1 and sys.argv[1] in _SKIP_COMMANDS:
            return

        # En desarrollo con autoreloader: solo iniciar en el proceso hijo (RUN_MAIN=true)
        # En producción (gunicorn/wsgi): RUN_MAIN no existe, siempre debe iniciar
        run_main = os.environ.get("RUN_MAIN", "")
        is_dev = "runserver" in sys.argv

        if is_dev and run_main != "true":
            return

        from apps.core.scheduler import start_scheduler
        start_scheduler()
