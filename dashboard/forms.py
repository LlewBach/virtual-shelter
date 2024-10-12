from django import forms
from .models import Sprite

class SpriteForm(forms.ModelForm):
    """
    Form for creating or updating a Sprite instance.

    Includes the fields 'breed' and 'colour' from the Sprite model.
    """
    class Meta:
        model = Sprite
        fields = ['breed', 'colour']

