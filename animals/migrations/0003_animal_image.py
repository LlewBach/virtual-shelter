# Generated by Django 5.1 on 2024-09-08 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0002_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
