from django.db import models
from datetime import datetime
from embed_video.fields import EmbedVideoField
from django.core.validators import RegexValidator


class Home(models.Model):
    name = models.CharField("Nazwa domu", max_length=100, null=False, blank=False)
    address = models.CharField("Adres", max_length=50, null=False, blank=False)
    zip_code = models.CharField("Kod pocztowy", max_length=50, null=False, blank=False)
    city = models.CharField("Miasto", max_length=50, null=False, blank=False)
    phone_number = models.CharField("Numer telefonu", max_length=15, null=False, blank=False,
                                    validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    nip = models.CharField("NIP", max_length=12, null=False, blank=False)
    regon = models.IntegerField("Regon", null=False, blank=False)
    page_url = models.CharField("Adres strony internetowej", max_length=50, null=False, blank=False)
    email_address = models.CharField("Adres e-mail", max_length=30, null=False, blank=False)

    def __str__(self):
        return self.name+" "+self.city

    class Meta:
        verbose_name = "Dom rekolekcyjny"
        verbose_name_plural = "Dom rekolekcyjny"

    def save(self, *args, **kwargs):
        if Home.objects.exists() and not self.pk:
            home = Home.objects.all()
            home.delete()
            self.pk = 1
        super(Home, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Congregation(models.Model):
    congregation = models.CharField("Nazwa zgromadzenia", max_length=100, null=False, blank=False)
    chief = models.CharField("Kierownik zgromadzenia", max_length=50, null=False, blank=False)
    community = models.CharField("Wspólnota", max_length=30, null=False, blank=False)
    director = models.CharField("Kierownik wspólnoty", max_length=50, null=False, blank=False)
    main_institution = models.CharField("Siedziba", max_length=100, null=False, blank=False)
    rodo = models.DateTimeField("Wersja RODO z dnia", null=False, blank=False)

    def __str__(self):
        return self.congregation

    class Meta:
        verbose_name = "Zgromadzenie"
        verbose_name_plural = "Zgromadzenie"

    def save(self, *args, **kwargs):
        if Congregation.objects.exists() and not self.pk:
            congregation = Congregation.objects.all()
            congregation.delete()
            self.pk = 1
        super(Congregation, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Room(models.Model):
    FLOORS = (
        (-1, '-1'),
        (0, '0'),
        (1, '1'),
        (2, '2'),
    )
    number = models.CharField("Numer", max_length=4, null=False, blank=False)
    beds_number = models.IntegerField("Liczba łóżek", null=False, blank=False)
    floor_number = models.IntegerField("Piętro", null=False, blank=False, choices=FLOORS)
    has_bathroom = models.BooleanField("Jest łazienka?", null=False, blank=False)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "Pokój"
        verbose_name_plural = "Pokoje"


class Booking(models.Model):
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    phone_number = models.CharField("Numer telefonu", max_length=15, null=False, blank=False,
                                    validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    email_address = models.EmailField("Adres e-mail", max_length=40, null=False, blank=False)
    room = models.ManyToManyField(Room, verbose_name="Pokoje", blank=True)
    begin_date = models.DateTimeField("Data początkowa", null=False, blank=False)
    end_date = models.DateTimeField("Data końcowa", null=False, blank=False)
    adults = models.IntegerField("Dorośli/młodzież", null=True, blank=True, default=1)
    kids = models.IntegerField("Dzieci", null=True, blank=True, default=0)
    meals = models.BooleanField("Posiłki", default=True, blank=True)
    full_cost = models.FloatField("Pełna kwota", default=0, blank=True)
    is_paid = models.BooleanField("Zapłacono", default=False, blank=False)
    installment = models.FloatField("Kwota zaliczki", default=0, blank=True)  # zaliczka
    is_part_paid = models.BooleanField("Zapłacona zaliczka", default=False, blank=False)
    who_where = models.TextField("Kto? Gdzie? (JSON)", max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Rezerwacja"
        verbose_name_plural = "Rezerwacje"


class Photo(models.Model):
    title = models.CharField("Tytuł", max_length=100, null=False, blank=False)
    image = models.ImageField("Obraz", upload_to="gallery", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Zdjęcie na stronie"
        verbose_name_plural = "Zdjęcia na stronie"


class Post(models.Model):
    title = models.CharField("Tytuł", max_length=100, null=False, blank=False)
    content = models.TextField("Treść", max_length=10000, null=False, blank=False)
    date = models.DateTimeField("Data", default=datetime.now, null=False, blank=False)
    photo = models.ManyToManyField(Photo, verbose_name="Obrazy", blank=True)
    video = EmbedVideoField("Video", blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Post na stronie"
        verbose_name_plural = "Posty na stronie"


class Price(models.Model):
    service = models.CharField("Usługa (bez spacji, na końcu bez znaków specjalnych)", max_length=100, null=False,
                               blank=False)
    price = models.FloatField("Cena", null=False, blank=False, default=0)

    def __str__(self):
        return self.service

    class Meta:
        verbose_name = "Cena"
        verbose_name_plural = "Ceny"


class File(models.Model):
    title = models.CharField("Nazwa", max_length=100, null=False, blank=False)
    upload = models.FileField("Plik", upload_to='uploads/', null=False, blank=False)
    volunteers = models.BooleanField("Wolontariusze", default=False, blank=False)
    coordinators = models.BooleanField("Koordynatorzy", default=False, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Plik"
        verbose_name_plural = "Pliki"
