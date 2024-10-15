from django.contrib import admin
from .models import Animal


class AnimalAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Animal model.

    Displays the shelter, image, name, species, breed, age, and adoption status
    in the list display of the admin interface.
    """
    list_display = (
        'shelter',
        'image',
        'name',
        'species',
        'breed',
        'age',
        'adoption_status'
        )


admin.site.register(Animal)
