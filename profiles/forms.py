from django import forms
from .models import RoleChangeRequest

class RoleChangeRequestForm(forms.ModelForm):
    class Meta:
        model = RoleChangeRequest
        fields = ['charity_name', 'charity_registration_number', 'charity_website', 'charity_description']
        widgets = {
            'charity_description': forms.Textarea(attrs={'rows': 4}),
        }
