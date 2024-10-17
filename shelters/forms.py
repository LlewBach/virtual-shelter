from django import forms
from .models import Shelter


class ShelterForm(forms.ModelForm):
    """
    A form for creating and updating Shelter instances, including fields for
    image, name, registration number, website, and description.
    """
    class Meta:
        model = Shelter
        fields = [
            'image',
            'name',
            'registration_number',
            'website',
            'description'
        ]
