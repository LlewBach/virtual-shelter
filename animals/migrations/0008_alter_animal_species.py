# Generated by Django 5.1 on 2024-10-11 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0007_alter_animal_adoption_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='species',
            field=models.CharField(choices=[('Dog', 'Dog')], max_length=100),
        ),
    ]