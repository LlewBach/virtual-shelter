# Generated by Django 5.1 on 2024-10-06 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0004_alter_animal_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
