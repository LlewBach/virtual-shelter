from django.apps import AppConfig


class SheltersConfig(AppConfig):
    """
    Configuration class for the 'shelters' app. Automatically imports signals when the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shelters'

    def ready(self):
        """
        Import shelters signals when the app is ready.
        """
        import shelters.signals
