from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """
    App configuration for the 'profiles' app.
    
    Sets the default auto field and imports signal handlers when the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        import profiles.signals
