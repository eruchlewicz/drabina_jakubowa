# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-01-05 16:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coordinatepanel', '0002_auto_20181227_1441'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='priest',
            name='address',
        ),
        migrations.RemoveField(
            model_name='priest',
            name='city',
        ),
        migrations.RemoveField(
            model_name='priest',
            name='email_address',
        ),
        migrations.RemoveField(
            model_name='priest',
            name='pesel',
        ),
        migrations.RemoveField(
            model_name='priest',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='priest',
            name='zip_code',
        ),
    ]
