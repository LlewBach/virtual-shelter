from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Shelter
from profiles.models import RoleChangeRequest

@receiver(post_save, sender=RoleChangeRequest)
def create_shelter_on_approval(sender, instance, created, **kwargs):
    if instance.status == 'approved':
        # Check if a shelter already exists for this user
        if not Shelter.objects.filter(admin=instance.user).exists():
            Shelter.objects.create(
                admin = instance.user,
                name = instance.charity_name,
                registration_number = instance.charity_registration_number,
                website = instance.charity_website,
                description = instance.charity_description,
            )
