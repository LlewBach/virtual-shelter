from django.db import models
from django.contrib.auth.models import User

class Shelter(models.Model):
    """
    A model representing a shelter, which includes an admin (a single User), an optional image,
    the shelter's name, registration number, website (optional), and a description of the shelter.
    """
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='', blank=True, null=True)
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        """
        Returns the string representation of the shelter, which is its name.
        """
        return self.name
