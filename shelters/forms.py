from django import forms
from .models import Shelter

class ShelterForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = ['name', 'registration_number', 'website', 'description']