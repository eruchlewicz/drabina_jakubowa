# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-13 18:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dj', '0003_auto_20190213_1913'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Image',
            new_name='Photo',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='image',
            new_name='photo',
        ),
    ]
