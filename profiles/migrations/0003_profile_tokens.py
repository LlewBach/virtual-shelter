# Generated by Django 5.1 on 2024-09-27 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_rolechangerequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='tokens',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
