from django.apps import AppConfig
import os


class TicketAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticket_app'


class TicketAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ticket_app"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return
        try:
            from .scheduler import start
            start()
        except Exception:
            pass