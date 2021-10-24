# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-10-23 22:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinatepanel', '0026_auto_20211023_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchparticipant',
            name='photographing_agreement',
            field=models.BooleanField(default=True, verbose_name='Zgoda na fotografowanie'),
        ),
        migrations.AlterField(
            model_name='batchparticipant',
            name='payment_id',
            field=models.CharField(default='#965575492', max_length=15, verbose_name='ID Płatności'),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='payment_id',
            field=models.CharField(default='#435731598', max_length=15, verbose_name='ID Płatności'),
        ),
    ]