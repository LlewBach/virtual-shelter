# Generated by Django 5.1 on 2024-10-06 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelters', '0002_shelter_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shelter',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]