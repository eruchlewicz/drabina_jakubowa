# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-07-10 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinatepanel', '0014_auto_20190709_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchparticipant',
            name='payment_id',
            field=models.CharField(default='#737127481', max_length=15, verbose_name='ID Płatności'),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='payment_id',
            field=models.CharField(default='#954252589', max_length=15, verbose_name='ID Płatności'),
        ),
    ]
