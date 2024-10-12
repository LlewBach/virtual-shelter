from django.apps import AppConfig


class AnimalsConfig(AppConfig):
    """
    Configuration for the Animals app.
    
    Specifies the default primary key type and the app name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'animals'
