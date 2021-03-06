# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-10-28 15:42
from __future__ import unicode_literals

import datetime
import django.core.validators
from django.db import migrations, models
import embed_video.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='Imię')),
                ('surname', models.CharField(max_length=30, verbose_name='Nazwisko')),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$')], verbose_name='Numer telefonu')),
                ('email_address', models.EmailField(max_length=40, verbose_name='Adres e-mail')),
                ('begin_date', models.DateTimeField(verbose_name='Data początkowa')),
                ('end_date', models.DateTimeField(verbose_name='Data końcowa')),
                ('adults', models.IntegerField(blank=True, default=1, null=True, verbose_name='Dorośli/młodzież')),
                ('kids', models.IntegerField(blank=True, default=0, null=True, verbose_name='Dzieci')),
                ('meals', models.BooleanField(default=True, verbose_name='Posiłki')),
                ('full_cost', models.FloatField(blank=True, default=0, verbose_name='Pełna kwota')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Zapłacono')),
                ('installment', models.FloatField(blank=True, default=0, verbose_name='Kwota zaliczki')),
                ('is_part_paid', models.BooleanField(default=False, verbose_name='Zapłacona zaliczka')),
                ('who_where', models.TextField(blank=True, max_length=1024, null=True, verbose_name='Kto? Gdzie? (JSON)')),
            ],
            options={
                'verbose_name': 'Rezerwacja',
                'verbose_name_plural': 'Rezerwacje',
            },
        ),
        migrations.CreateModel(
            name='Congregation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('congregation', models.CharField(max_length=100, verbose_name='Nazwa zgromadzenia')),
                ('chief', models.CharField(max_length=50, verbose_name='Kierownik zgromadzenia')),
                ('community', models.CharField(max_length=30, verbose_name='Wspólnota')),
                ('director', models.CharField(max_length=50, verbose_name='Kierownik wspólnoty')),
                ('main_institution', models.CharField(max_length=100, verbose_name='Siedziba')),
            ],
            options={
                'verbose_name': 'Zgromadzenie',
                'verbose_name_plural': 'Zgromadzenie',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Nazwa')),
                ('upload', models.FileField(upload_to='uploads/', verbose_name='Plik')),
                ('volunteers', models.BooleanField(default=False, verbose_name='Wolontariusze')),
                ('coordinators', models.BooleanField(default=False, verbose_name='Koordynatorzy')),
            ],
            options={
                'verbose_name': 'Plik',
                'verbose_name_plural': 'Pliki',
            },
        ),
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nazwa domu')),
                ('address', models.CharField(max_length=50, verbose_name='Adres')),
                ('zip_code', models.CharField(max_length=50, verbose_name='Kod pocztowy')),
                ('city', models.CharField(max_length=50, verbose_name='Miasto')),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$')], verbose_name='Numer telefonu')),
                ('nip', models.CharField(max_length=12, verbose_name='NIP')),
                ('regon', models.IntegerField(verbose_name='Regon')),
                ('page_url', models.CharField(max_length=50, verbose_name='Adres strony internetowej')),
                ('email_address', models.CharField(max_length=30, verbose_name='Adres e-mail')),
            ],
            options={
                'verbose_name': 'Dom rekolekcyjny',
                'verbose_name_plural': 'Dom rekolekcyjny',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Tytuł')),
                ('content', models.TextField(max_length=10000, verbose_name='Treść')),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Data')),
                ('image', models.ImageField(blank=True, null=True, upload_to='gallery', verbose_name='Obraz')),
                ('video', embed_video.fields.EmbedVideoField(blank=True, null=True, verbose_name='Video')),
            ],
            options={
                'verbose_name': 'Post na stronie',
                'verbose_name_plural': 'Posty na stronie',
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=100, verbose_name='Usługa (bez spacji, na końcu bez znaków specjalnych)')),
                ('price', models.FloatField(default=0, verbose_name='Cena')),
            ],
            options={
                'verbose_name': 'Cena',
                'verbose_name_plural': 'Ceny',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=4, verbose_name='Numer')),
                ('beds_number', models.IntegerField(verbose_name='Liczba łóżek')),
                ('floor_number', models.IntegerField(choices=[(-1, '-1'), (0, '0'), (1, '1'), (2, '2')], verbose_name='Piętro')),
                ('has_bathroom', models.BooleanField(verbose_name='Jest łazienka?')),
            ],
            options={
                'verbose_name': 'Pokój',
                'verbose_name_plural': 'Pokoje',
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='room',
            field=models.ManyToManyField(blank=True, to='dj.Room', verbose_name='Pokoje'),
        ),
    ]
