from django import forms
from .models import Profile, RoleChangeRequest


class ProfileForm(forms.ModelForm):
    """
    A form for updating a user's profile information.

    This form allows users to update their profile picture and bio.
    It is associated with the `Profile` model.
    """
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']


class RoleChangeRequestForm(forms.ModelForm):
    """
    A form for users to submit a request to change their role to Shelter Admin.

    This form is associated with the `RoleChangeRequest` model and allows users
    to provide details about the charity they represent when requesting a role
    change. It includes fields for the charity's name, registration number,
    website, and a description. A custom widget is used for the
    `charity_description` field to provide a larger text area with 4 rows for
    input.
    """
    class Meta:
        model = RoleChangeRequest
        fields = [
            'charity_name',
            'charity_registration_number',
            'charity_website',
            'charity_description'
            ]
        widgets = {
            'charity_description': forms.Textarea(attrs={'rows': 4}),
        }
