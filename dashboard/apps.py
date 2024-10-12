from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """
    Configuration class for the 'dashboard' app.

    Sets the default auto field type and specifies the app name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
