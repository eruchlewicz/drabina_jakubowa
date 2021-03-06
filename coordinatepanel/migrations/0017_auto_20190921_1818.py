# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-09-21 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coordinatepanel', '0016_auto_20190814_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='father_first_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Imię ojca'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='mother_first_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Imię matki'),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='mother_surname',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Nazwisko panieńskie matki'),
        ),
        migrations.AlterField(
            model_name='batchparticipant',
            name='payment_id',
            field=models.CharField(default='#762439220', max_length=15, verbose_name='ID Płatności'),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='payment_id',
            field=models.CharField(default='#316486558', max_length=15, verbose_name='ID Płatności'),
        ),
        migrations.AlterField(
            model_name='eventvolunteer',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='evvol', to='coordinatepanel.Event', verbose_name='Wydarzenie'),
            preserve_default=False,
        ),
    ]
