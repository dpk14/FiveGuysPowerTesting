# Generated by Django 3.1.5 on 2021-02-09 05:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrument',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='instruments', to='database.equipmentmodel'),
        ),
    ]
