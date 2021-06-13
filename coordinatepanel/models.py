from django.db import models
from django.core.validators import RegexValidator
from dj.models import Room
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from fernet_fields import *
from random import randrange

now = timezone.now()


class Director(models.Model):
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    phone_number = models.CharField("Numer telefonu", max_length=15, null=False, blank=False,
                                    validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    email_address = models.EmailField("Adres e-mail", max_length=40, null=False, blank=False)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Dyrektor"
        verbose_name_plural = "Dyrektorzy"


class Institution(models.Model):
    name = models.TextField("Nazwa", max_length=100, null=False, blank=False)
    director = models.ForeignKey(Director, verbose_name="Dyrektor", null=False, blank=False)
    city = models.CharField("Miasto", max_length=40, null=False, blank=False)
    zip_code = models.CharField("Kod pocztowy", max_length=6, null=False, blank=False)
    address = models.CharField("Adres", max_length=30, null=False, blank=False)

    def __str__(self):
        return self.name + " " + self.city

    class Meta:
        verbose_name = "Placówka"
        verbose_name_plural = "Placówki"


class Volunteer(models.Model):
    SEX = (
        ('K', 'Kobieta'),
        ('M', 'Mężczyzna'),
    )
    AGE = (
        ("ZM", 'Nie mam skończonych 16 lat'),  # za młody
        ("M", 'Skończone 16 lat'),  # młodzież
        ("D", 'Skończone 18 lat'),  # dorosły
    )
    EDUCATION = (
        ("P", 'Podstawowe'),
        ("G", 'Gimnazjalne'),
        ("S", 'Średnie'),
        ("Z", 'Zawodowe'),
        ("PM", 'Pomaturalne'),
        ("W", 'Wyższe'),
        ("I", 'Inne'),
    )
    HOW_KNOW = (
        ("Z", 'Od znajomych wolontariuszy'),
        ("P", 'Od znajomych podopiecznych'),
        ("RP", 'Z rekolekcji parafialnych'),
        ("K", 'Z kościoła'),
        ("D", 'Ze spotkania w moim duszpasterstwie'),
        ("AD", 'Z Anielskiej Domówki'),
        ("US", 'Z uczelni lub ze szkoły'),
        ("FB", 'Z Facebooka'),
        ("TV", 'Z radia, TV, prasy'),
        ("S", 'Z tej strony internetowej'),
        ("YT", 'Z filmu na YouTube'),
        ("I", 'Inne'),
    )
    DRUGS = (
        ("T", 'Tak'),
        ("N", 'Nie'),
    )
    user = models.ForeignKey(User, verbose_name="Użytkownik", null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    pesel = models.CharField("PESEL", max_length=11, null=False, blank=False,
                             validators=[RegexValidator(regex='^[0-9]{11}$ || ^$')])
    sex = models.CharField("Płeć", max_length=1, null=False, blank=False, choices=SEX)
    age = models.CharField("Wiek", max_length=2, null=False, blank=False, choices=AGE)
    phone_number = models.CharField("Numer telefonu", max_length=15, null=False, blank=False,
                                    validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    email_address = models.EmailField("Adres e-mail", max_length=40, null=False, blank=False)
    city = models.CharField("Miasto", max_length=40, null=False, blank=False)
    zip_code = models.CharField("Kod pocztowy", max_length=6, null=False, blank=False)
    address = models.CharField("Adres", max_length=30, null=False, blank=False)
    education = models.CharField("Wykształcenie", max_length=2, null=False, blank=False, choices=EDUCATION)
    is_first_time = models.BooleanField("Pierwszy raz", default=True, blank=False)
    how_know_dj = models.CharField("Skąd znasz DJ?", max_length=2, null=False, blank=False, choices=HOW_KNOW)
    description = models.TextField("Opis", max_length=250, null=True, blank=True)
    data_processing_agreement = models.BooleanField("Zgoda na przetwarzanie danych osobowych", default=False,
                                                    blank=False, null=False)
    photographing_agreement = models.BooleanField("Zgoda na fotografowanie", default=False, blank=True, null=False)
    study = models.BooleanField("Uczę sie", default=False, blank=True, null=False)
    work = models.BooleanField("Pracuję", default=False, blank=True, null=False)
    babysitting = models.BooleanField("Opiekuję się dziećmi", default=False, blank=True, null=False)
    pensioner = models.BooleanField("Jestem emerytem/rencistą", default=False, blank=True, null=False)
    unemployed = models.BooleanField("Jestem bezrobotny", default=False, blank=True, null=False)
    another_work = models.TextField("Inne zajęcie", max_length=100, null=True, blank=True)
    physical_health = models.BooleanField("Zdrowie fizyczne", default=False, blank=False, null=False)
    mental_health = models.BooleanField("Zdrowie psychiczne", default=False, blank=False, null=False)
    drugs = models.CharField("Czy przyjmujesz leki?", max_length=2, default=1, null=False, blank=False, choices=DRUGS)
    guardian_phone_number = models.CharField("Numer telefonu opiekuna", max_length=15, null=False, blank=False,
                                             validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    first_air_training = models.BooleanField("Szkolenie z pierwszej pomocy", default=False, blank=True, null=False)
    sanitary_book = models.BooleanField("Książeczka sanepidowska", default=False, blank=True, null=False)
    training_courses = models.TextField("Inne szkolenia i kursy", max_length=200, null=True, blank=True)
    experience_with_disabled = models.BooleanField("Doświadczenie z niepełnosprawnymi", default=False, blank=True,
                                                   null=False)
    easy_going = models.BooleanField("Łatwość w nawiązywaniu kontaktu z ludźmi", default=False, blank=True, null=False)
    teamwork = models.BooleanField("Odnajduję się w pracy zespołowej", default=False, blank=True, null=False)
    entertaining = models.BooleanField("Potrafię zorganizować czas innym, zaprosić do zabawy", default=False,
                                       blank=True, null=False)
    sing_or_play = models.BooleanField("Gram lub śpiewam", default=False, blank=True, null=False)
    photographing = models.BooleanField("Fotografuję", default=False, blank=True, null=False)
    writing_articles = models.BooleanField("Piszę artykuły", default=False, blank=True, null=False)
    it = models.BooleanField("Zajmuję się IT i mediami społecznościowymi", default=False, blank=True, null=False)
    tidiness = models.BooleanField("Utrzymuję porządek", default=False, blank=True, null=False)
    photo = models.ImageField("Zdjęcie", upload_to="gallery", null=True, blank=True)
    mother_first_name = models.CharField("Imię matki", max_length=100, null=True, blank=True)
    mother_surname = models.CharField("Nazwisko panieńskie matki", max_length=100, null=True, blank=True)
    father_first_name = models.CharField("Imię ojca", max_length=100, null=True, blank=True)
    family_name = models.CharField("Nazwisko rodowe", max_length=100, null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Wolontariusz"
        verbose_name_plural = "Wolontariusze"


class Priest(models.Model):
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Ksiądz"
        verbose_name_plural = "Księża"


class Coordinator(models.Model):
    user = models.OneToOneField(User, verbose_name="Użytkownik", on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField("Imię", max_length=100, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=100, null=False, blank=False)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Koordynator"
        verbose_name_plural = "Koordynatorzy"


class Nurse(models.Model):
    user = models.OneToOneField(User, verbose_name="Użytkownik", on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", related_name="nurvol", null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Pielęgniarz"
        verbose_name_plural = "Pielęgniarze"


class Doctor(models.Model):
    user = models.OneToOneField(User, verbose_name="Użytkownik", on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", related_name="docvol", null=True, blank=True)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Lekarz"
        verbose_name_plural = "Lekarze"


class Batch(models.Model):
    name = models.TextField("Nazwa", max_length=50, null=False, blank=False)
    institution = models.ForeignKey(Institution, verbose_name="Placówka", null=False, blank=False)
    main_priest = models.ForeignKey(Priest, verbose_name="Rekolekcjonista", null=True, blank=True)
    auxiliary_priest = models.ForeignKey(Priest, verbose_name="Rekolekcjonista p.", null=True,
                                         blank=True, related_name="auxiliary_priest")
    main_coordinator = models.ForeignKey(Coordinator, verbose_name="Koordynator", null=True, blank=True)
    main_coordinator_was_there = models.BooleanField("Koordynator był na turnusie", default=False, blank=True,
                                                     null=False)
    auxiliary_coordinator = models.ForeignKey(Coordinator, verbose_name="Koordynator p.", null=True,
                                              blank=True, related_name="auxiliary_coordinator")
    auxiliary_coordinator_was_there = models.BooleanField("Koordynator pomocniczy był na turnusie", default=False,
                                                          blank=True, null=False)
    begin_date = models.DateTimeField("Data rozpoczęcia", null=False, blank=False)
    end_date = models.DateTimeField("Data zakończenia", null=False, blank=False)
    training_duration = models.IntegerField("Szkolenie (h)", default=14, blank=True)
    volunteers = models.IntegerField("Liczba wolontariuszy", default=0, blank=True)
    participants = models.IntegerField("Liczba podopiecznych", default=0, blank=True)
    nurse = models.ManyToManyField(Nurse, verbose_name="Pielęgniarze", blank=True)
    doctor = models.ManyToManyField(Doctor, verbose_name="Lekarze", blank=True)
    batch_price = models.FloatField("Koszt pobytu", default=700, blank=True)
    is_closed = models.BooleanField("Zapisy zamknięte", default=False, blank=True, null=False)

    def __str__(self):
        return self.name+" "+self.institution.city+" "+str(self.begin_date.year)

    class Meta:
        verbose_name = "Turnus"
        verbose_name_plural = "Turnusy"


class BatchVolunteer(models.Model):
    SEX = (
        ('K', 'Kobieta'),
        ('M', 'Mężczyzna'),
    )
    CATEGORY = (
        ('W', 'Wolontariusz'),
        ('P', 'Podopieczny'),
    )
    batch = models.ForeignKey(Batch, verbose_name="Turnus", related_name="batchvol", null=False, blank=False)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", related_name="vol", null=False, blank=False)
    room = models.ForeignKey(Room, verbose_name="Pokój", null=True, blank=True)
    room_sex = models.CharField("Płeć osób w pokoju", max_length=1, null=True, blank=True, choices=SEX)
    room_person_category = models.CharField("Kategoria pokoju", max_length=1, null=True, blank=True, choices=CATEGORY)
    batch_begin_date = models.DateTimeField("Data przyjazdu na turnus", null=True, blank=True)
    batch_end_date = models.DateTimeField("Data opuszczenia turnusu", null=True, blank=True)
    batch_days = models.IntegerField("Liczba dni spędzonych z podopiecznymi", default=10, blank=True)
    add_days = models.IntegerField("Liczba organizacyjnych dni przed turnusem (tylko koordynator)", default=0,
                                   blank=True)
    training_days = models.IntegerField("Ilość dni szkolenia (piątek, sobota)", default=2, blank=True)
    was_there = models.BooleanField("Wolontariusz pojawił się na turnusie", default=False, blank=True, null=False)
    nights = models.IntegerField("Liczba dyżurów nocnych", default=0, blank=True)
    daily_activities = models.BooleanField("pomoc w czynnościach codziennych, tj. pomoc w ubieraniu się, jedzeniu, "
                                           "myciu, poruszaniu się", default=False, blank=True, null=False)
    free_time_organise = models.BooleanField("organizacja czasu wolnego podopiecznym i wolontariuszom", default=False,
                                             blank=True, null=False)
    sport_activities = models.BooleanField("zajęcia sportowo – rekreacyjne dla wszystkich uczestników wyjazdu",
                                           default=False, blank=True, null=False)
    games_organise = models.BooleanField("organizowanie i prowadzenie gier, zabaw, konkursów w terenie jak i w "
                                         "budynku ośrodka", default=False, blank=True, null=False)
    walking_trips = models.BooleanField("wycieczki piesze po okolicy", default=False, blank=True, null=False)
    physical_activities = models.BooleanField("udział w zajęciach ruchowych, integracyjnych, orientacyjnych w obszarze "
                                              "wolontariusz-podopieczny", default=False, blank=True, null=False)
    games_mobilisation = models.BooleanField("aktywizowanie podopiecznych przez włączanie ich do zabaw ruchowych i "
                                             "intelektualnych", default=False, blank=True, null=False)
    night_shift = models.BooleanField("nocny dyżur w celu opiekuńczo-kontrolnym wszystkich podopiecznych",
                                      default=False, blank=True, null=False)
    kitchen_cleaning = models.BooleanField("pomoc w pracach kuchennych, utrzymaniu czystości stołówki", default=False,
                                           blank=True, null=False)
    general_cleaning = models.BooleanField("dbanie o czystość na terenie ośrodka (pokoje podopiecznych, łazienki, "
                                           "korytarze)", default=False, blank=True, null=False)
    music_classes = models.BooleanField("prowadzenie spotkań umuzykalniających", default=False, blank=True, null=False)
    photographing = models.BooleanField("tworzenie fotoreportażu podczas turnusu", default=False, blank=True,
                                        null=False)
    funpage = models.BooleanField("uaktualnianie strony internetowej, fanpage'a na Facebook'u itp.", default=False,
                                  blank=True, null=False)
    savoir_vivre = models.BooleanField("udział w szkoleniu wolontariuszy z zakresu savoir-vivre z niepełnosprawnymi",
                                       default=False, blank=True, null=False)
    care_training = models.BooleanField("udział w szkoleniu wolontariuszy z zakresu pielęgnacji osób niepełnosprawnych "
                                        "i starszych", default=False, blank=True, null=False)
    unique_key = models.UUIDField("Unikalny klucz", default=uuid.uuid4, editable=False, unique=True)
    reserve_list = models.BooleanField("Lista rezerwowa", default=False, blank=False)
    note = models.TextField("Notatka", max_length=500, null=True, blank=True)
    sign_date = models.DateTimeField("Kiedy zapisano", default=timezone.now, null=False, blank=True)
    participant_helper = models.BooleanField("Pomoc przy popdopiecznych", default=False, blank=False)
    checked = models.BooleanField("Sprawdzony w rejestrze", default=False, blank=False)

    def __str__(self):
        return self.batch.name+" "+str(self.batch.begin_date.year)+" "+self.batch.institution.city+" "\
               + self.volunteer.first_name + " " + self.volunteer.surname

    class Meta:
        verbose_name = "Wolontariusz na turnusie"
        verbose_name_plural = "Turnus - wolontariusz"


class Participant(models.Model):
    COMMUNICATION = (
        ("OK", 'Narcyz'),
        ("TR", 'Kaktus'),
        ("KS", 'Fikus'),
        ("MI", 'Hiacynt'),
        ("N", 'Róża'),
    )
    SEX = (
        ('K', 'Kobieta'),
        ('M', 'Mężczyzna'),
    )
    HOW_KNOW = (
        ("Z", 'Od znajomych wolontariuszy'),
        ("P", 'Od znajomych podopiecznych'),
        ("RP", 'Z rekolekcji parafialnych'),
        ("K", 'Z kościoła'),
        ("D", 'Ze spotkania w moim duszpasterstwie'),
        ("AD", 'Z Anielskiej Domówki'),
        ("US", 'Z uczelni lub ze szkoły'),
        ("FB", 'Z Facebooka'),
        ("TV", 'Z radia, TV, prasy'),
        ("S", 'Z tej strony internetowej'),
        ("YT", 'Z filmu na YouTube'),
        ("I", 'Inne'),
    )
    DRUGS = (
        ("T", 'Tak'),
        ("N", 'Nie'),
        ("BD", 'Brak danych'),
    )
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    pesel = models.CharField("PESEL", max_length=11, null=False, blank=False,
                             validators=[RegexValidator(regex='^[0-9]{11}$ || ^$')])
    sex = models.CharField("Płeć", max_length=1, null=False, blank=False, choices=SEX)
    phone_number = models.CharField("Numer telefonu", max_length=15, null=True, blank=True,
                                    validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    guardian_name = models.CharField("Imię i nazwisko opiekuna", max_length=50, null=True, blank=True)
    guardian_phone_number = models.CharField("Numer telefonu opiekuna", max_length=15, null=True, blank=True,
                                             validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])  # telefon opiekuna
    email_address = models.EmailField("Adres e-mail", max_length=40, null=True, blank=True)
    city = models.CharField("Miasto", max_length=40, null=False, blank=False)
    zip_code = models.CharField("Kod pocztowy", max_length=6, null=False, blank=False)
    address = models.CharField("Adres", max_length=50, null=False, blank=False)
    flower= models.CharField("Kwiatek", max_length=2, null=False, blank=False, choices=COMMUNICATION)
    others= EncryptedTextField("Inne", max_length=500, null=True, blank=True)
    photo = models.ImageField("Zdjęcie", upload_to="gallery", null=True, blank=True)
    foundation = models.TextField("Dane fundacji np. do wystawienia zaświadczenia", max_length=200, null=True,
                                  blank=True)
    how_know_dj = models.CharField("Skąd zna DJ?", max_length=2, null=False, blank=False, choices=HOW_KNOW)
    is_first_time = models.BooleanField("Pierwszy raz", default=True, blank=False)
    candies = models.CharField("Czy je słodycze?", max_length=2, default=1, null=False, blank=False, choices=DRUGS)
    cat = models.BooleanField("Kot", default=False, blank=False)
    dog = models.BooleanField("Pies", default=False,
                              blank=False)
    bear = models.BooleanField("Miś", default=False, blank=False)
    monkey = models.BooleanField("Małpka", default=False, blank=False)
    frog = models.BooleanField("Żaba", default=False, blank=False)
    bat = models.BooleanField("Nietoperz", default=False, blank=False)
    spider = models.BooleanField("Pająk", default=False, blank=False)
    fish = models.BooleanField("Ryba", default=False, blank=False)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Podopieczny"
        verbose_name_plural = "Podopieczni"


class BatchParticipant(models.Model):
    SEX = (
        ('K', 'Kobieta'),
        ('M', 'Mężczyzna'),
    )
    CATEGORY = (
        ('W', 'Wolontariusz'),
        ('P', 'Podopieczny'),
    )
    PAYMENT_METHOD = (
        ('G', 'Gotówka'),
        ('K', 'Karta płatnicza'),
        ('P', 'Przelew bankowy'),
    )
    batch = models.ForeignKey(Batch, verbose_name="Turnus", related_name="batchpar", null=False, blank=False)
    participant = models.ForeignKey(Participant, verbose_name="Podopieczny", null=False, blank=False)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", null=True, blank=True)
    installment = models.FloatField("Kwota zaliczki", default=100, blank=True)  # zaliczka
    is_part_paid = models.BooleanField("Zapłacono zaliczkę", default=False, blank=False)
    full_cost = models.FloatField("Pełny koszt", default=700, blank=True)
    is_paid = models.BooleanField("Zapłacono", default=False, blank=False)
    payment_method = models.CharField("Metoda płatności", max_length=1, null=True, blank=True, choices=PAYMENT_METHOD)
    payment_id = models.CharField("ID Płatności", default="#"+str(randrange(100000000, 999999999)), max_length=15)
    room = models.ForeignKey(Room, verbose_name="Pokój", null=True, blank=True)
    room_sex = models.CharField("Płeć osób w pokoju", max_length=1, null=True, blank=True, choices=SEX)
    room_person_category = models.CharField("Kategoria pokoju", max_length=1, null=True, blank=True, choices=CATEGORY)
    batch_begin_date = models.DateTimeField("Data przyjazdu na turnus", null=True, blank=True)
    batch_end_date = models.DateTimeField("Data opuszczenia turnusu", null=True, blank=True)
    unique_key = models.UUIDField("Unikalny klucz", default=uuid.uuid4, editable=False, unique=True)
    reserve_list = models.BooleanField("Lista rezerwowa", default=False, blank=False)
    note = models.TextField("Notatka", max_length=500, null=True, blank=True)
    sign_date = models.DateTimeField("Kiedy zapisano", default=timezone.now, null=False, blank=True)

    def __str__(self):
        return self.batch.name+" "+str(self.batch.begin_date.year)+" "+self.batch.institution.city+" "\
               + self.participant.first_name + " " + self.participant.surname

    class Meta:
        verbose_name = "Podopieczny na turnusie"
        verbose_name_plural = "Turnus - podopieczny"


class Event(models.Model):
    name = models.CharField("Nazwa", max_length=50, null=False, blank=False)
    main_coordinator = models.ForeignKey(Coordinator, verbose_name="Koordynator", null=True, blank=True,
                                         related_name="ev_coo")
    auxiliary_coordinator = models.ForeignKey(Coordinator, verbose_name="Koordynator p.", null=True, blank=True)
    begin_date = models.DateTimeField("Data rozpoczęcia", null=False, blank=False)
    end_date = models.DateTimeField("Data zakończenia", null=False, blank=False)
    volunteers = models.IntegerField("Liczba wolontariuszy", default=0, blank=True)
    participants = models.IntegerField("Liczba podopiecznych", default=0, blank=True)
    nurse = models.ManyToManyField(Nurse, verbose_name="Pielęgniarze", blank=True)
    doctor = models.ManyToManyField(Doctor, verbose_name="Lekarze", blank=True)
    info = models.TextField("Informacje", max_length=5000, null=True, blank=True)
    price = models.FloatField("Koszt", default=0, blank=True)
    is_closed = models.BooleanField("Zapisy zamknięte", default=False, blank=True, null=False)

    def __str__(self):
        if self.begin_date.year == self.end_date.year:
            return self.name+" "+str(self.begin_date.year)
        else:
            return self.name+" "+str(self.begin_date.year)+"/"+str(self.end_date.year)

    class Meta:
        verbose_name = "Wydarzenie"
        verbose_name_plural = "Wydarzenia"


class EventVolunteer(models.Model):
    event = models.ForeignKey(Event, verbose_name="Wydarzenie", related_name="evvol", null=False, blank=False)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", related_name="volo", null=False, blank=False)
    total_cost = models.FloatField("Pełny koszt", default=0, blank=True)
    is_paid = models.BooleanField("Zapłacono", default=False, blank=True, null=False)
    sign_date = models.DateTimeField("Kiedy zapisano", default=timezone.now, null=False, blank=True)
    payment_id = models.CharField("ID Płatności", default="#wy0w0", max_length=15)
    was_there = models.BooleanField("Wolontariusz pojawił się na wydarzeniu", default=False, blank=True, null=False)

    def __str__(self):
        return self.event.name+" "+str(self.event.begin_date.year)+" "+self.volunteer.first_name + " " + \
               self.volunteer.surname

    class Meta:
        verbose_name = "Wolontariusz na wydarzeniu"
        verbose_name_plural = "Wydarzenie - wolontariusz"


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, verbose_name="Wydarzenie", related_name="evpartic", null=False, blank=False)
    participant = models.ForeignKey(Participant, verbose_name="Podopieczny", related_name="partic", null=False,
                                    blank=False)
    total_cost = models.FloatField("Pełny koszt", default=0, blank=True)
    is_paid = models.BooleanField("Zapłacono", default=False, blank=True, null=False)
    payment_id = models.CharField("ID Płatności", default="#"+str(randrange(100000000, 999999999)), max_length=15)
    sign_date = models.DateTimeField("Kiedy zapisano", default=timezone.now, null=False, blank=True)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", null=True, blank=True)

    def __str__(self):
        return self.event.name+" "+str(self.event.begin_date.year)+" "+self.participant.first_name + " "\
               + self.participant.surname

    class Meta:
        verbose_name = "Podopieczny na wydarzeniu"
        verbose_name_plural = "Wydarzenie - podopieczny"


class RetreatOrMusicTraining(models.Model):
    TYPE = (
        ('R', 'Rekolekcje'),
        ('W', 'Warsztaty'),
        ('M', 'Warsztaty muzyczne'),
    )
    name = models.CharField("Nazwa", max_length=50, null=False, blank=False)
    institution = models.ForeignKey(Institution, verbose_name="Placówka", null=True, blank=True)
    main_coordinator = models.ForeignKey(Coordinator, verbose_name="Koordynator", null=True, blank=True,
                                         related_name="music_coo")
    auxiliary_coordinator = models.ForeignKey(Coordinator, verbose_name="Koordynator pomocniczy", null=True, blank=True)
    begin_date = models.DateTimeField("Data rozpoczęcia", null=False, blank=False)
    end_date = models.DateTimeField("Data zakończenia", null=False, blank=False)
    people = models.IntegerField("Liczba uczestników", default=0, blank=True)
    info = models.TextField("Informacje", max_length=250, null=True, blank=True)
    type = models.CharField("Typ", max_length=1, null=False, blank=False, choices=TYPE)
    with_accommodation = models.BooleanField("Zapewniony nocleg", default=False, blank=True, null=False)
    with_additional_night = models.BooleanField("Możliwość dodatkowego noclegu po wydarzeniu", default=False,
                                                blank=True, null=False)
    base_price = models.FloatField("Cena bazowa", default=0, blank=True)
    sleeping_bag_price = models.FloatField("Cena z własnym śpiworem", default=0, blank=True)
    nights_price = models.FloatField("Cena z noclegiem", default=0, blank=True)
    additional_night = models.FloatField("Dodatkowy nocleg", default=0, blank=True)
    is_closed = models.BooleanField("Zapisy zamknięte", default=False, blank=True, null=False)

    def __str__(self):
        return self.name+" "+str(self.begin_date.year)

    class Meta:
        verbose_name = "Warsztaty/rekolekcje"
        verbose_name_plural = "Warsztaty/rekolekcje"


class Person(models.Model):
    SEX = (
        ('K', 'Kobieta'),
        ('M', 'Mężczyzna'),
    )
    AGE = (
        ("ZM", 'Nie mam skończonych 16 lat'),  # za młody
        ("M", 'Skończone 16 lat'),  # młodzież
        ("D", 'Skończone 18 lat'),  # dorosły
    )
    EDUCATION = (
        ("P", 'Podstawowe'),
        ("G", 'Gimnazjalne'),
        ("S", 'Średnie'),
        ("Z", 'Zawodowe'),
        ("PM", 'Pomaturalne'),
        ("W", 'Wyższe'),
        ("I", 'Inne'),
    )
    HOW_KNOW = (
        ("Z", 'Od znajomych wolontariuszy'),
        ("P", 'Od znajomych podopiecznych'),
        ("RP", 'Z rekolekcji parafialnych'),
        ("K", 'Z kościoła'),
        ("D", 'Ze spotkania w moim duszpasterstwie'),
        ("AD", 'Z Anielskiej Domówki'),
        ("US", 'Z uczelni lub ze szkoły'),
        ("FB", 'Z Facebooka'),
        ("TV", 'Z radia, TV, prasy'),
        ("S", 'Z tej strony internetowej'),
        ("YT", 'Z filmu na YouTube'),
        ("I", 'Inne'),
    )
    first_name = models.CharField("Imię", max_length=30, null=False, blank=False)
    surname = models.CharField("Nazwisko", max_length=30, null=False, blank=False)
    pesel = models.CharField("PESEL", max_length=11, null=False, blank=False,
                             validators=[RegexValidator(regex='^[0-9]{11}$ || ^$')])
    sex = models.CharField("Płeć", max_length=1, null=False, blank=False, choices=SEX)
    age = models.CharField("Wiek", max_length=2, null=False, blank=False, choices=AGE)
    city = models.CharField("Miasto", max_length=40, null=False, blank=False)
    zip_code = models.CharField("Kod pocztowy", max_length=6, null=True, blank=True)
    address = models.CharField("Adres", max_length=30, null=True, blank=True)
    phone_number = models.CharField("Numer telefonu", max_length=15, null=False, blank=False,
                                    validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    email_address = models.EmailField("Adres e-mail", max_length=40, null=False, blank=False)
    education = models.CharField("Wykształcenie", max_length=2, null=True, blank=True, choices=EDUCATION)

    def __str__(self):
        return self.first_name + " " + self.surname

    class Meta:
        verbose_name = "Uczestnik"
        verbose_name_plural = "Uczestnik"


class RetreatOrMusicTrainingPerson(models.Model):
    SEX = (
        ('K', 'Kobieta'),
        ('M', 'Mężczyzna'),
    )
    HOW_KNOW = (
        ("Z", 'Od znajomych wolontariuszy'),
        ("P", 'Od znajomych podopiecznych'),
        ("RP", 'Z rekolekcji parafialnych'),
        ("K", 'Z kościoła'),
        ("D", 'Ze spotkania w moim duszpasterstwie'),
        ("AD", 'Z Anielskiej Domówki'),
        ("US", 'Z uczelni lub ze szkoły'),
        ("FB", 'Z Facebooka'),
        ("TV", 'Z radia, TV, prasy'),
        ("S", 'Z tej strony internetowej'),
        ("YT", 'Z filmu na YouTube'),
        ("I", 'Inne'),
    )
    YESNO = (
        ("T", 'Tak'),
        ("N", 'Nie'),
    )
    VOICE = (
        ("S", 'Sopran'),
        ("A", 'Alt'),
        ("T", 'Tenor'),
        ("B", 'Bas'),
        ("N", 'Nie wiem'),
    )
    ACCOMMODATION = (
        ("N", 'Nie potrzebuję noclegu, mieszkam niedaleko'),
        ("S", 'Mam śpiwór i materac, potrzebuję tylko miejsca do spania'),
        ("L", 'Chcę się wygodnie wyspać i mogę za to zapłacić'),
    )
    STAY = (
        ("T", 'Tak, zostanę na śniadanie i wspólną Mszę'),
        ("N", 'Nie, wracam nocą do domu'),
    )
    retreat_or_music_training = models.ForeignKey(RetreatOrMusicTraining, verbose_name="Warsztaty/rekolekcje",
                                                  related_name="train_person", null=False, blank=False)
    person = models.ForeignKey(Person, verbose_name="Uczestnik", related_name="person_train", null=True, blank=True)
    volunteer = models.ForeignKey(Volunteer, verbose_name="Wolontariusz", related_name="v", null=True, blank=True)
    room = models.ForeignKey(Room, verbose_name="Pokój", null=True, blank=True)
    room_sex = models.CharField("Płeć osób w pokoju", max_length=1, null=True, blank=True, choices=SEX)
    how_know_training = models.CharField("Skąd dowiedziałeś/aś się o warsztatach?", max_length=2, null=True,
                                         blank=True, choices=HOW_KNOW)
    description = models.TextField("Dodatkowe informacje", max_length=250, null=True, blank=True)
    voice = models.CharField("Głos", max_length=2, null=True, blank=True, choices=VOICE)
    experience = models.CharField("Doświadczenie sceniczne", max_length=2, null=True, blank=True, choices=YESNO)
    instrument = models.CharField("Instrument", max_length=30, null=True, blank=True)
    is_first_time = models.BooleanField("Pierwszy raz na rekolekcjach", default=True, blank=True)
    how_know_dj = models.CharField("Skąd znasz DJ?", max_length=2, null=True, blank=True, choices=HOW_KNOW)
    study = models.BooleanField("Uczę sie", default=False, blank=True)
    work = models.BooleanField("Pracuję", default=False, blank=True)
    babysitting = models.BooleanField("Opiekuję się dziećmi", default=False, blank=True)
    pensioner = models.BooleanField("Jestem emerytem/rencistą", default=False, blank=True)
    unemployed = models.BooleanField("Jestem bezrobotny", default=False, blank=True)
    another_work = models.TextField("Inne zajęcie", max_length=100, null=True, blank=True)
    guardian_phone_number = models.CharField("Numer telefonu opiekuna", max_length=15, null=True, blank=True,
                                             validators=[RegexValidator(regex='^\+?1?\d{9,15}$')])
    communion = models.BooleanField("Duszpasterstwo", default=False, blank=True)
    communion_description = models.TextField("Jakie wspólnoty/duszpasterstwa", max_length=250, null=True, blank=True)
    sing_or_play = models.BooleanField("Gram lub śpiewam", default=False, blank=True)
    description_why = models.TextField("Dlaczego chcesz zostać animatorem", max_length=250, null=True, blank=True)
    accommodation = models.CharField("Opcja noclegu", max_length=2, null=False, blank=False, choices=ACCOMMODATION)
    saturday_sunday = models.CharField("Nocleg sobota/niedziela", default='N', max_length=2, null=False, blank=False,
                                       choices=STAY)
    total_cost = models.FloatField("Pełny koszt", default=0, blank=True)
    is_paid = models.BooleanField("Zapłacono", default=False, blank=True, null=False)
    data_processing_agreement = models.BooleanField("Zgoda na przetwarzanie danych osobowych", default=False,
                                                    blank=False, null=False)
    photographing_agreement = models.BooleanField("Zgoda na fotografowanie", default=False, blank=True, null=False)
    sign_date = models.DateTimeField("Kiedy zapisano", default=timezone.now, null=False, blank=True)
    payment_id = models.CharField("ID Płatności", default="#wrwm0i0", max_length=15)
    was_there = models.BooleanField("Osoba pojawiła się na warsztatach lub rekolekcjach", default=False, blank=True,
                                    null=False)

    def __str__(self):
        return self.retreat_or_music_training.name+" "+str(self.retreat_or_music_training.begin_date.year)+" "\
               + self.person.first_name + " " + self.person.surname

    class Meta:
        verbose_name = "Uczestnik warsztatów lub rekolekcji"
        verbose_name_plural = "Warsztaty/rekolekcje - uczestnik"


class EventPost(models.Model):
    title = models.CharField("Tytuł", max_length=100, null=True, blank=True)
    content = models.TextField("Opis", max_length=10000, null=False, blank=False)
    batch = models.ForeignKey(Batch, verbose_name="Turnus", null=True, blank=True)
    event = models.ForeignKey(Event, verbose_name="Wydarzenie", null=True, blank=True)
    retreat_or_music_training = models.ForeignKey(RetreatOrMusicTraining, verbose_name="Rekolekcje/Warsztaty",
                                                  null=True, blank=True)
    photo = models.ImageField("Zdjęcie", upload_to="gallery", null=True, blank=True)
    begin_date = models.DateTimeField("Data rozpoczęcia", null=True, blank=True)

    def __str__(self):
        if self.title is not None:
            return self.title
        elif self.batch is not None:
            return self.batch.name
        elif self.event is not None:
            return self.event.name
        else:
            return self.retreat_or_music_training.name

    def save(self, *args, **kwargs):
        if self.batch is not None:
            self.begin_date = self.batch.begin_date
        if self.event is not None:
            self.begin_date = self.event.begin_date
        if self.retreat_or_music_training is not None:
            self.begin_date = self.retreat_or_music_training.begin_date
        super(EventPost, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Post wydarzenia"
        verbose_name_plural = "Posty wydarzeń"
