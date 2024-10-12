from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    """
    Model for user profile.

    Attributes:
    -----------
    user: 
        A one-to-one relationship with Django User model.
    role: 
        Either 'user', 'shelter_admin', or 'superuser'.
    tokens: 
        Number of virtual tokens the user has.
    bio: 
        Optional text field for user's bio.
    profile_picture: 
        Optional image field for the user's profile.
    """
    
    USER_ROLES = (
        ('user', 'User'),
        ('shelter_admin', 'Shelter Admin'),
        ('superuser', 'Superuser')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')
    tokens = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='', blank=True, null=True)

    def __str__(self):
        """
        Returns string representation of Profile object.
        """
        return f'Profile of {self.user.username}'


class RoleChangeRequest(models.Model):
    """
    Model for role change requests.

    Stores information about a user's request to change their role to become a shelter admin. This includes details about the charity the user represents, such as name, registration 
    number, website, and description. The status of the request (pending, approved, or rejected) is tracked as well.

    Attributes:
    -----------
        user: 
            The user making the role change request.
        charity_name: 
            The name of the charity.
        charity_registration_number: 
            The registration number of the charity.
        charity_website: 
            Optional field for the charity's website URL.
        charity_description: 
            A description of the charity.
        status: 
            The status of the request, which can be 'pending', 'approved', or 'rejected'.
    """
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

    def __str__(self):
        """
        Returns string representation of RoleChangeRequest object.
        """
        return f'{self.user.username} - {self.charity_name} - {self.status}'