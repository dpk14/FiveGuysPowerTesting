# Generated by Django 3.1.5 on 2021-02-06 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0006_auto_20210205_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='vendor',
            field=models.CharField(default=None, max_length=30),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.TextField(default=None, unique=True),
        ),
    ]