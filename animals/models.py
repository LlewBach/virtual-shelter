from django.db import models
from shelters.models import Shelter
from profiles.models import Profile


class Animal(models.Model):
    """
    Represents an animal in the system, associated with a shelter and optionally a fosterer.

    Attributes:
        shelter (ForeignKey): 
            The shelter that the animal belongs to.
        fosterer (ForeignKey): 
            The profile of the fosterer, if applicable.
        image: 
            Optional image of the animal.
        name: 
            The name of the animal.
        species : 
            The species of the animal, with 'Dog' as a default choice.
        breed: 
            The breed of the animal, which is optional.
        age: 
            The age of the animal.
        description: 
            Optional description of the animal.
        adoption_status: 
            The current adoption status of the animal.
    """

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
        """
        Returns string representation of Animal object.
        """
        return f'{self.name} - {self.shelter}'


class Update(models.Model):
    """
    Represents an update related to a specific animal.

    Attributes:
        animal (ForeignKey):
            The animal that this update is associated with.
        text: 
            The content of the update.
        created_at: 
            The date and time when the update was created, automatically set on creation.
    """
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='updates')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns string representation of Update object.
        """
        return f'Update for {self.animal.name} on {self.created_at.strftime("%Y-%m-%d")}'
