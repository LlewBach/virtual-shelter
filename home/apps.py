from django.apps import AppConfig


class HomeConfig(AppConfig):
    """
    Configuration class for the 'home' app. Sets the default primary key field
    type and specifies the app's name as 'home'.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
