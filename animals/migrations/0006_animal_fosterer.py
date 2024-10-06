# Generated by Django 5.1 on 2024-10-06 18:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0005_alter_animal_image'),
        ('profiles', '0003_profile_tokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='fosterer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='animals', to='profiles.profile'),
        ),
    ]
