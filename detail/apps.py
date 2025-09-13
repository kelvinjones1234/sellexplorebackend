from django.apps import AppConfig


class DetailConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "detail"

    def ready(self):
        """
        This method is called when the app is ready. It's the standard
        place to import signal handlers to ensure they are connected
        only once.
        """
        import detail.signals
