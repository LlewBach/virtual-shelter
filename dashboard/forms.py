from django import forms
from .models import Sprite

class SpriteForm(forms.ModelForm):
    class Meta:
        model = Sprite
        fields = ['sprite_sheet']

