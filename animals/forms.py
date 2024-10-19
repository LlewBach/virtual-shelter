from django import forms
from .models import Animal, Update


class AnimalForm(forms.ModelForm):
    """
    Form for creating or updating an Animal instance.

    Includes a custom age field with specific choices for age ranges.
    """
    AGE_CHOICES = [
        ('0-5 month', '0-5 months'),
        ('6-12 month', '6-12 months'),
        ('1 year', '1 year'),
        ('2 year', '2 years'),
        ('3 year', '3 years'),
        ('4 year', '4 years'),
        ('5 year', '5 years'),
        ('6 year', '6 years'),
        ('7 year', '7 years'),
        ('8 year', '8 years'),
        ('9 year', '9 years'),
        ('10 year', '10 years'),
        ('11 year', '11 years'),
        ('12 year', '12 years'),
        ('13 year', '13 years'),
        ('14 year', '14 years'),
        ('15 year', '15 years'),
        ('16 year', '16 years'),
        ('17 year', '17 years'),
        ('18 year', '18 years'),
        ('19 year', '19 years'),
        ('20 year', '20 years'),
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
