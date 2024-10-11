from django.db import models
from shelters.models import Shelter
from profiles.models import Profile


class Animal(models.Model):
    class SpeciesChoices(models.TextChoices):
        DOG = 'Dog', 'Dog'

    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='animals')
    fosterer = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='animals', blank=True, null=True)
    image = models.ImageField(upload_to='', blank=True, null=True)
    name = models.CharField(max_length=255)
    species = models.CharField(max_length=25, choices=SpeciesChoices.choices, default=SpeciesChoices.DOG)
    breed = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    adoption_status = models.CharField(max_length=20, choices=[('Available', 'Available'), ('Fostered', 'Fostered')], default='Available')

    def __str__(self):
        return f'{self.name} - {self.shelter}'


class Update(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='updates')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Update for {self.animal.name} on {self.created_at.strftime("%Y-%m-%d")}'
