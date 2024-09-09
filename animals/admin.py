from django.contrib import admin
from .models import Animal

class AnimalAdmin(admin.ModelAdmin):
    list_display = ('shelter', 'image', 'name', 'species', 'breed', 'age', 'adoption_status')

admin.site.register(Animal)
