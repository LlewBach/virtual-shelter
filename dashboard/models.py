from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from animals.models import Animal


class Sprite(models.Model):
    """
    Model representing a virtual sprite associated with an animal.

    Includes breed, color, status, and timing information for standing or
    running states. Each sprite is tied to a user and an animal.
    """
    class BreedChoices(models.TextChoices):
        HUSKY = 'husky', 'Husky'
        AFGHAN = 'afghan', 'Afghan'
        BLOODHOUND = 'bloodhound', 'Bloodhound'
        GREYHOUND = 'greyhound', 'Greyhound'
        SHIBA = 'shiba', 'Shiba'
        ALSATIAN = 'alsatian', 'Alsatian'
        DALMATIAN = 'dalmatian', 'Dalmatian'
        DOBERMAN = 'doberman', 'Doberman'
        GREATDANE = 'greatdane', 'Greatdane'

    class ColourChoices(models.TextChoices):
        ONE = 'one', 'Colour 1'
        TWO = 'two', 'Colour 2'
        THREE = 'three', 'Colour 3'

    class States(models.TextChoices):
        STANDING = 'STANDING', 'Standing'
        RUNNING = 'RUNNING', 'Running'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sprites'
        )
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    breed = models.CharField(
        max_length=50,
        choices=BreedChoices.choices,
        default=BreedChoices.HUSKY
        )
    colour = models.CharField(
        max_length=50,
        choices=ColourChoices.choices,
        default=ColourChoices.ONE
        )
    url = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now=True)
    satiation = models.IntegerField(default=50)
    current_state = models.CharField(
        max_length=10,
        choices=States.choices,
        default=States.STANDING
    )
    time_standing = models.IntegerField(default=0)
    time_running = models.IntegerField(default=0)

    def __str__(self):
        """
        Returns a string representation of the sprite, including the associated
        animal's name.
        """
        return f"Sprite {self.id} for {self.animal.name}"

    def update_status(self):
        """
        Updates the sprite's status based on time elapsed since last checked.

        Adjusts the sprite's satiation, state (standing or running), and time
        spent in each state. Resets daily time counters if a new day has begun.
        """
        now = timezone.now()
        delta = now - self.last_checked
        mins_passed = delta.seconds // 60

        self.satiation = max(self.satiation - mins_passed, 0)

        # Reset time values if it's a new day
        if self.last_checked.date() != now.date():
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            self.last_checked = midnight
            self.time_standing = 0
            self.time_running = 0

            delta = now - self.last_checked
            mins_passed = delta.seconds // 60

        # State time setters
        if self.current_state == self.States.STANDING:
            self.time_standing += mins_passed
        elif self.current_state == self.States.RUNNING:
            self.time_running += mins_passed

        # State change handlers
        if self.satiation < 50:
            self.current_state = self.States.STANDING
        else:
            self.current_state = self.States.RUNNING

        self.last_checked = now
        self.save()
