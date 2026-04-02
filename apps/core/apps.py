import os
import sys
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        # No iniciar el scheduler en comandos de gestión (migrate, collectstatic, etc.)
        is_management = len(sys.argv) > 1 and sys.argv[1] not in ("runserver", "shell")
        if is_management:
            return

        # En desarrollo con autoreloader: solo iniciar en el proceso hijo (RUN_MAIN=true)
        # En producción (gunicorn): RUN_MAIN no está definido, así que siempre inicia
        run_main = os.environ.get("RUN_MAIN", "")
        is_dev = "runserver" in sys.argv

        if is_dev and run_main != "true":
            return

        from apps.core.scheduler import start_scheduler
        start_scheduler()
