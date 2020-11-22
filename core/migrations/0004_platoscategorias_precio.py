# Generated by Django 3.0.6 on 2020-07-10 12:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200703_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='platoscategorias',
            name='precio',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.RegexValidator(message='Enter a valid value', regex='^[0-9]+$'), django.core.validators.MaxValueValidator(9999)]),
            preserve_default=False,
        ),
    ]