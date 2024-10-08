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
    tokens = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    # profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class RoleChangeRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    charity_name = models.CharField(max_length=255)
    charity_registration_number = models.CharField(max_length=100)
    charity_website = models.URLField(blank=True, null=True)
    charity_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.charity_name} - {self.status}'