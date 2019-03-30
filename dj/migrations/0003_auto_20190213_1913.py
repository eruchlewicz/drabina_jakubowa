# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2019-02-13 18:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dj', '0002_congregation_rodo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Tytuł')),
                ('image', models.ImageField(blank=True, null=True, upload_to='gallery', verbose_name='Obraz')),
            ],
            options={
                'verbose_name': 'Zdjęcie na stronie',
                'verbose_name_plural': 'Zdjęcia na stronie',
            },
        ),
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ManyToManyField(blank=True, to='dj.Image', verbose_name='Obrazy'),
        ),
    ]
