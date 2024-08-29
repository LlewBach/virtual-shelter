from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    USER_ROLES = (
        ('user', 'User'),
        ('shelter_admin', 'Shelter Admin'),
        ('superuser', 'Superuser')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')
    # bio = models.TextField(blank=True)
    # profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'