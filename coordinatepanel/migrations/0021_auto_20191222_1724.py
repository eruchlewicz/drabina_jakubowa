# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-12-22 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinatepanel', '0020_auto_20191217_0849'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchvolunteer',
            name='checked',
            field=models.BooleanField(default=False, verbose_name='Sprawdzony w rejestrze'),
        ),
        migrations.AlterField(
            model_name='batchparticipant',
            name='payment_id',
            field=models.CharField(default='#599607136', max_length=15, verbose_name='ID Płatności'),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='payment_id',
            field=models.CharField(default='#712826205', max_length=15, verbose_name='ID Płatności'),
        ),
    ]