# Generated by Django 5.1 on 2024-09-08 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sprite',
            name='breed',
            field=models.CharField(choices=[('husky', 'Husky'), ('afghan', 'Afghan')], default='husky', max_length=50),
        ),
        migrations.AlterField(
            model_name='sprite',
            name='sprite_sheet',
            field=models.CharField(max_length=50),
        ),
    ]