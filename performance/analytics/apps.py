from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Analytics & Forecasting'

    def ready(self):
        # Register signal handlers
        from . import signals  # noqa
