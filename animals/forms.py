from django import forms
from .models import Animal, Update


class AnimalForm(forms.ModelForm):
    """
    Form for creating or updating an Animal instance.

    Includes a custom age field with specific choices for age ranges.
    """
    AGE_CHOICES = [
        (0, '0-5 months'),
        (1, '6-12 months'),
        (2, '1 year'),
        (3, '2 years'),
        (4, '3 years'),
        (5, '4 years'),
        (6, '5 years'),
        (7, '6 years'),
        (8, '7 years'),
        (9, '8 years'),
        (10, '9 years'),
        (11, '10 years'),
        (12, '11 years'),
        (13, '12 years'),
        (14, '13 years'),
        (15, '14 years'),
        (16, '15 years'),
        (17, '16 years'),
        (18, '17 years'),
        (19, '18 years'),
        (20, '19 years'),
        (21, '20 years'),
    ]

    age = forms.ChoiceField(choices=AGE_CHOICES, label="Age")

    class Meta:
        model = Animal
        fields = [
            'image',
            'name',
            'species',
            'breed',
            'age',
            'description',
            'adoption_status'
            ]


class UpdateForm(forms.ModelForm):
    """
    Form for creating or updating an Update instance.

    Only includes a field for the update text.
    """
    class Meta:
        model = Update
        fields = ['text']
