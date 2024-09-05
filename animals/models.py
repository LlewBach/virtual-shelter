from django.db import models
from shelters.models import Shelter


class Animal(models.Model):
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='animals')
    name = models.CharField(max_length=255)
    species = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    adoption_status = models.CharField(max_length=20, choices=[('available', 'Available'), ('fostered', 'Fostered')], default='available')

    def __str__(self):
        return f'{self.name} - {self.shelter}'


class Update(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='updates')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Update for {self.animal.name} on {self.created_at.strftime("%Y-%m-%d")}'
