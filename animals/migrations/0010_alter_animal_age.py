# Generated by Django 5.1 on 2024-10-19 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0009_alter_animal_species'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='age',
            field=models.CharField(max_length=15),
        ),
    ]
