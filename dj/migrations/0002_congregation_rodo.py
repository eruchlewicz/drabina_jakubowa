# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-10 20:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dj', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='congregation',
            name='rodo',
            field=models.DateTimeField(default='2018-11-17', verbose_name='Wersja RODO z dnia'),
            preserve_default=False,
        ),
    ]
