# Generated by Django 3.1.5 on 2021-01-29 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='calibration_frequency',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
