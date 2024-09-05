from django import forms
from .models import Animal, Update

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'species', 'breed', 'age', 'description', 'adoption_status']


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ['text']