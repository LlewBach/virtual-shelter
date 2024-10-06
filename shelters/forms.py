from django import forms
from .models import Shelter

class ShelterForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = ['image', 'name', 'registration_number', 'website', 'description']