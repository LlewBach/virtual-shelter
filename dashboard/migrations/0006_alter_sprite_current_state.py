# Generated by Django 5.1 on 2024-09-25 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_sprite_current_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprite',
            name='current_state',
            field=models.CharField(choices=[('STANDING', 'Standing'), ('RUNNING', 'Running')], default='STANDING', max_length=10),
        ),
    ]
