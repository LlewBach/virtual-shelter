from django import forms
from .models import Profile, RoleChangeRequest


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']


class RoleChangeRequestForm(forms.ModelForm):
    class Meta:
        model = RoleChangeRequest
        fields = ['charity_name', 'charity_registration_number', 'charity_website', 'charity_description']
        widgets = {
            'charity_description': forms.Textarea(attrs={'rows': 4}),
        }
