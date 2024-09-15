from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from animals.models import Animal

class Sprite(models.Model):
    class BreedChoices(models.TextChoices):
        HUSKY = 'husky', 'Husky'
        AFGHAN = 'afghan', 'Afghan'

    class ColourChoices(models.TextChoices):
        ONE = 'one', 'Colour 1'
        TWO = 'two', 'Colour 2'
        THREE = 'three', 'Colour 3'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sprites')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    breed = models.CharField(max_length=50, choices=BreedChoices.choices, default=BreedChoices.HUSKY)
    colour = models.CharField(max_length=50, choices=ColourChoices.choices, default=ColourChoices.ONE)
    url = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now=True)
    satiation = models.IntegerField(default=50)
    # energy = models.IntegerField(default=50)
    # current_state = models.CharField(
    #     max_length=10, 
    #     choices=States.choices, 
    #     default=States.SLEEPING
    # )


    def __str__(self):
        return f"Sprite {self.id} for {self.animal.name}"

    def update_status(self):
        """Update the status based on time elapsed since last check."""
        now = timezone.now()
        delta = now - self.last_checked

        # Decrease satiation by 1 point every min
        mins_passed = delta.seconds // 60
        # self.satiation = 97

        self.satiation = max(self.satiation - mins_passed, 0)
        self.last_checked = now
        self.save()

    # def feed(self):
    #     """Feed the Tamagotchi to increase satiation."""
    #     self.hunger = min(100, self.hunger + 20)
    #     self.update_status()

    # def play(self):
    #     """Play with the Tamagotchi to increase happiness."""
    #     if self.hunger > 20:  # Can only play if not too hungry
    #         self.happiness = min(100, self.happiness + 10)
    #     self.update_status()
