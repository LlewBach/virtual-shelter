# Generated by Django 5.1 on 2024-09-30 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_sprite_current_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprite',
            name='time_running',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sprite',
            name='time_standing',
            field=models.IntegerField(default=0),
        ),
    ]
