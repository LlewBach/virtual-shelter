from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Profile, RoleChangeRequest


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a Profile instance when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Save the Profile instance whenever the User is saved.
    """
    instance.profile.save()


@receiver(post_save, sender=RoleChangeRequest)
def notify_superuser_on_role_change_request(
    sender, instance, created, **kwargs
):
    """
    Notify superusers via email when a new RoleChangeRequest is created.
    """
    if created:
        # Fetch the superuser
        User = get_user_model()
        superusers = User.objects.filter(is_superuser=True)

        # Prepare email details
        subject = "New Shelter Admin Role Change Request"
        message = (
            f"A new role change request by {instance.user.username}.\n\n"
            f"Details:\nCharity Name: {instance.charity_name}\n"
            f"Registration Number: {instance.charity_registration_number}\n"
            f"Website: {instance.charity_website}\n"
            f"Description: {instance.charity_description}\n\n"
            f"Please review the request in the admin panel."
            )

        # Send the email to all superusers
        for superuser in superusers:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [superuser.email]
            )
