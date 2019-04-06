from django import forms
from coordinatepanel.models import *
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField
import re


class SetVolunteerPhotoForm(forms.ModelForm):

    class Meta:
        model = Volunteer
        fields = ['photo']
        labels = {
            'photo': _('Zdjęcie'),
        }

    def clean(self):
        cleaned_data = super(SetVolunteerPhotoForm, self).clean()
        photo = cleaned_data.get('photo')
        if photo:
            if photo.size > 1024 * 1024 / 2:
                msg = _("Plik jest za duży (max. 500 KB).")
                self.errors["photo"] = self.error_class([msg])


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Hasło", help_text="Hasło powinno mieć min. 8 znaków, "
                                                                                    "przynajmniej jedną cyfrę i znak "
                                                                                    "specjalny")
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label="Powtórz hasło")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirmation', 'first_name', 'last_name']
        labels = {
            'username': _('Nazwa użytkownika'),
            'email': _('Adres e-mail'),
            'first_name': _('Imię'),
            'last_name': _('Nazwisko'),
        }
        help_texts = {
            'username': '',
            'email': 'Bardzo ważny dla dalszej komunikacji'
        }

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        cleaned_username = cleaned_data.get('username')
        cleaned_first_name = cleaned_data.get('first_name')
        cleaned_last_name = cleaned_data.get('last_name')
        cleaned_email_address = cleaned_data.get('email')
        cleaned_password = cleaned_data.get('password')
        cleaned_password_confirmation = cleaned_data.get('password_confirmation')
        special_sym = ['!', '@', '#', '$', '%', "^", "&", "*", "(", ")", ".", ",", "/", "?", ":", ";", "[", "]", "_",
                       "-", "+", "=", "{", "}", "|", "'", "\"", "\\"]

        if User.objects.filter(username=cleaned_username).first():
            msg = _("Użytkownik o tej nazwie już istnieje.")
            self.errors["pesel"] = self.error_class([msg])

        if len(cleaned_email_address) == 0:
            msg = _("Pole jest wymagane.")
            self.errors["email"] = self.error_class([msg])
        elif "." not in str(cleaned_email_address):
            msg = _("Adres e-mail jest niepoprawny.")
            self.errors["email"] = self.error_class([msg])

        if not len(cleaned_password) >= 8:
            msg = _("Hasło powinno mieć co najmniej 8 znaków.")
            self.errors["password"] = self.error_class([msg])
        elif not any(char.isdigit() for char in cleaned_password):
            msg = _("Hasło powinno mieć zawierać przynajmniej jedną cyfrę.")
            self.errors["password"] = self.error_class([msg])
        elif not any(char in special_sym for char in cleaned_password):
            msg = _("Hasło powinno zawierać przynajmniej jeden znak specjalny.")
            self.errors["password"] = self.error_class([msg])

        if not cleaned_password == cleaned_password_confirmation:
            msg = _("Hasła nie są jednakowe.")
            self.errors["password_confirmation"] = self.error_class([msg])

        if not cleaned_first_name:
            msg = _("Pole jest wymagane.")
            self.errors["first_name"] = self.error_class([msg])

        if not cleaned_last_name:
            msg = _("Pole jest wymagane.")
            self.errors["last_name"] = self.error_class([msg])


class VolunteerForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Volunteer
        fields = ['sex', 'pesel', 'age', 'phone_number', 'city', 'zip_code', 'address',
                  'education', 'is_first_time', 'how_know_dj', 'study', 'work', 'babysitting', 'pensioner',
                  'unemployed', 'another_work', 'physical_health', 'mental_health', 'drugs', 'guardian_phone_number',
                  'first_air_training', 'sanitary_book', 'training_courses', 'experience_with_disabled', 'easy_going',
                  'teamwork', 'entertaining', 'sing_or_play', 'photographing', 'writing_articles', 'it', 'tidiness',
                  'description', 'data_processing_agreement', 'photographing_agreement']
        labels = {
            'sex': _('Płeć'),
            'pesel': _('PESEL'),
            'age': _('Wiek'),
            'phone_number': _('Numer telefonu'),
            'city': _('Miejscowość'),
            'zip_code': _('Kod pocztowy'),
            'address': _('Adres zamieszkania'),
            'education': _('Wykształcenie'),
            'is_first_time': _('Będę pierwszy raz na Drabinie Jakubowej'),
            'description': _('Kilka słów o sobie'),
            'data_processing_agreement': _('Wyrażam zgodę na przetwarzanie moich danych osobowych'),
            'photographing_agreement': _('Wyrażam zgodę na fotografowanie i przetwarzanie wizerunku'),
            'how_know_dj': _('Skąd dowiedziałeś/aś się o Drabinie Jakubowej?'),
            'study': _('Uczę się'),
            'work': _('Pracuję'),
            'babysitting': _('Opiekuję się dziećmi'),
            'pensioner': _('Jestem rencistą, emerytem'),
            'unemployed': _('Jestem bezrobotny/a'),
            'another_work': _('Inne zajęcie'),
            'physical_health': _('Mój stan zdrowia fizycznego pozwala mi na to, by brać udział w turnusie jako '
                                 'wolontariusz'),
            'mental_health': _('Mój stan zdrowia psychicznego pozwala mi na to, by być wolontariuszem w takim miejscu'),
            'drugs': _('Czy musisz regularnie przyjmować leki?'),
            'guardian_phone_number': _('Numer telefonu osoby, którą będziemy mogli powiadomić w przypadku Twoich '
                                       'problemów ze zdrowiem'),
            'first_air_training': _('Posiadam szkolenie z udzielania pierwszej pomocy'),
            'sanitary_book': _('Posiadam aktualną książeczkę sanepidowską'),
            'training_courses': _('Szkolenia/kursy, które mogą przydać się w pracy jako wolontariusz'),
            'experience_with_disabled': _('Mam doświadczenie w pracy z niepełnosprawnymi'),
            'easy_going': _('Mam łatwość w nawiązywaniu kontaktu z ludźmi, również chorymi'),
            'teamwork': _('Dobrze odnajduję się w pracy zespołowej'),
            'entertaining': _('Umiem zorganizować czas innym, zaprosić do wspólnej zabawy itp.'),
            'sing_or_play': _('Gram lub śpiewam'),
            'photographing': _('Zajmuję się fotografowaniem'),
            'writing_articles': _('Lubię i umiem pisać artykuły'),
            'it': _('Znam się na IT, programuję, obsługuję YT, FB, Twitter'),
            'tidiness': _('Lubię i potrafię utrzymać porządek'),
        }
        help_texts = {
            'pesel': 'Będzie nam potrzebny m.in. do ubezpieczenia',
            'description': "Dlaczego chcesz zostać wolontariuszem, jakie masz zainteresowania, umiejętności, itp."
        }

    def clean(self):
        cleaned_data = super(VolunteerForm, self).clean()
        cleaned_pesel = cleaned_data.get('pesel')
        cleaned_phone_number = cleaned_data.get('phone_number')
        cleaned_guardian_phone_number = cleaned_data.get('guardian_phone_number')
        cleaned_data_processing_agreement = cleaned_data.get('data_processing_agreement')
        cleaned_address = cleaned_data.get('address')
        cleaned_zip_code = cleaned_data.get('zip_code')
        cleaned_city = cleaned_data.get('city')
        cleaned_education = cleaned_data.get('education')
        cleaned_physical_health = cleaned_data.get('physical_health')
        cleaned_mental_health = cleaned_data.get('mental_health')

        if not re.match('^[0-9]{11}$', cleaned_pesel):
            msg = _("Nieprawidłowy PESEL.")
            self.errors["pesel"] = self.error_class([msg])
        elif int(cleaned_pesel[2]+cleaned_pesel[3]) > 32 or int(cleaned_pesel[4]+cleaned_pesel[5]) > 31:
            msg = _("Nieprawidłowy PESEL.")
            self.errors["pesel"] = self.error_class([msg])

        if cleaned_phone_number:
            if not re.match('^\+?1?\d{9,15}$', cleaned_phone_number):
                msg = _("Nieprawidłowy numer telefonu.")
                self.errors["phone_number"] = self.error_class([msg])

        if not re.match('^\+?1?\d{9,15}$', cleaned_guardian_phone_number):
            msg = _("Nieprawidłowy numer telefonu.")
            self.errors["guardian_phone_number"] = self.error_class([msg])

        if not cleaned_data_processing_agreement:
            msg = _("Pole jest wymagane.")
            self.errors["data_processing_agreement"] = self.error_class([msg])

        if not re.match('^(\w|[ .-])+ [1-9][0-9]*[a-zA-Z]?(/[1-9][0-9]*)?$', cleaned_address):
            msg = _("Nieprawidłowy adres.")
            self.errors["address"] = self.error_class([msg])

        if not re.match('^[0-9]{2}[-][0-9]{3}$', cleaned_zip_code):
            msg = _("Kod pocztowy jest niepoprawny.")
            self.errors["zip_code"] = self.error_class([msg])

        if not cleaned_city:
            msg = _("Pole jest wymagane.")
            self.errors["city"] = self.error_class([msg])

        if not cleaned_education:
            msg = _("Pole jest wymagane.")
            self.errors["education"] = self.error_class([msg])

        if not cleaned_physical_health:
            msg = _("Pole jest wymagane.")
            self.errors["physical_health"] = self.error_class([msg])

        if not cleaned_mental_health:
            msg = _("Pole jest wymagane.")
            self.errors["mental_health"] = self.error_class([msg])


class VolunteerEditForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ["first_name", 'surname', 'email_address', 'sex', 'pesel', 'age', 'phone_number', 'city', 'zip_code',
                  'address',
                  'education', 'study', 'work', 'babysitting', 'pensioner',
                  'unemployed', 'another_work', 'physical_health', 'mental_health', 'drugs', 'guardian_phone_number',
                  'first_air_training', 'sanitary_book', 'training_courses', 'experience_with_disabled', 'easy_going',
                  'teamwork', 'entertaining', 'sing_or_play', 'photographing', 'writing_articles', 'it', 'tidiness',
                  'description', 'photographing_agreement']
        labels = {
            'sex': _('Płeć'),
            "first_name": _('Imię'),
            'surname': _('Nazwisko'),
            'email_address': _('Adres e-mail'),
            'pesel': _('PESEL'),
            'age': _('Wiek'),
            'phone_number': _('Numer telefonu'),
            'city': _('Miejscowość'),
            'zip_code': _('Kod pocztowy'),
            'address': _('Adres zamieszkania'),
            'education': _('Wykształcenie'),
            'description': _('Kilka słów o sobie'),
            'photographing_agreement': _('Wyrażam zgodę na fotografowanie i przetwarzanie wizerunku'),
            'study': _('Uczę się'),
            'work': _('Pracuję'),
            'babysitting': _('Opiekuję się dziećmi'),
            'pensioner': _('Jestem rencistą, emerytem'),
            'unemployed': _('Jestem bezrobotny/a'),
            'another_work': _('Inne zajęcie'),
            'physical_health': _('Mój stan zdrowia fizycznego pozwala mi na to, by brać udział w turnusie jako '
                                 'wolontariusz'),
            'mental_health': _('Mój stan zdrowia psychicznego pozwala mi na to, by być wolontariuszem w takim miejscu'),
            'drugs': _('Czy musisz regularnie przyjmować leki?'),
            'guardian_phone_number': _('Numer telefonu osoby, którą będziemy mogli powiadomić w przypadku Twoich '
                                       'problemów ze zdrowiem'),
            'first_air_training': _('Posiadam szkolenie z udzielania pierwszej pomocy'),
            'sanitary_book': _('Posiadam aktualną książeczkę sanepidowską'),
            'training_courses': _('Szkolenia/kursy, które mogą przydać się w pracy jako wolontariusz'),
            'experience_with_disabled': _('Mam doświadczenie w pracy z niepełnosprawnymi'),
            'easy_going': _('Mam łatwość w nawiązywaniu kontaktu z ludźmi, również chorymi'),
            'teamwork': _('Dobrze odnajduję się w pracy zespołowej'),
            'entertaining': _('Umiem zorganizować czas innym, zaprosić do wspólnej zabawy itp.'),
            'sing_or_play': _('Gram lub śpiewam'),
            'photographing': _('Zajmuję się fotografowaniem'),
            'writing_articles': _('Lubię i umiem pisać artykuły'),
            'it': _('Znam się na IT, programuję, obsługuję YT, FB, Twitter'),
            'tidiness': _('Lubię i potrafię utrzymać porządek'),
        }

    def clean(self):
        cleaned_data = super(VolunteerEditForm, self).clean()
        cleaned_first_name = cleaned_data.get('first_name')
        cleaned_surname = cleaned_data.get('surname')
        cleaned_email_address = cleaned_data.get('email_address')
        cleaned_pesel = cleaned_data.get('pesel')
        cleaned_phone_number = cleaned_data.get('phone_number')
        cleaned_guardian_phone_number = cleaned_data.get('guardian_phone_number')
        cleaned_address = cleaned_data.get('address')
        cleaned_zip_code = cleaned_data.get('zip_code')
        cleaned_city = cleaned_data.get('city')
        cleaned_education = cleaned_data.get('education')
        cleaned_physical_health = cleaned_data.get('physical_health')
        cleaned_mental_health = cleaned_data.get('mental_health')

        if cleaned_email_address:
            if "." not in str(cleaned_email_address):
                msg = _("Adres e-mail jest niepoprawny.")
                self.errors["email_addresa"] = self.error_class([msg])
        else:
            msg = _("Adres e-mail jest niepoprawny.")
            self.errors["email_address"] = self.error_class([msg])

        if not cleaned_first_name:
            msg = _("Pole jest wymagane.")
            self.errors["first_name"] = self.error_class([msg])

        if not cleaned_surname:
            msg = _("Pole jest wymagane.")
            self.errors["surname"] = self.error_class([msg])

        if not re.match('^[0-9]{11}$', cleaned_pesel):
            msg = _("Nieprawidłowy PESEL.")
            self.errors["pesel"] = self.error_class([msg])

        if cleaned_phone_number:
            if not re.match('^\+?1?\d{9,15}$', cleaned_phone_number):
                msg = _("Nieprawidłowy numer telefonu.")
                self.errors["phone_number"] = self.error_class([msg])

        if not re.match('^\+?1?\d{9,15}$', cleaned_guardian_phone_number):
            msg = _("Nieprawidłowy numer telefonu.")
            self.errors["guardian_phone_number"] = self.error_class([msg])

        if not re.match('^(\w|[ .-])+ [1-9][0-9]*[a-zA-Z]?(/[1-9][0-9]*)?$', cleaned_address):
            msg = _("Nieprawidłowy adres.")
            self.errors["address"] = self.error_class([msg])

        if not re.match('^[0-9]{2}[-][0-9]{3}$', cleaned_zip_code):
            msg = _("Kod pocztowy jest niepoprawny.")
            self.errors["zip_code"] = self.error_class([msg])

        if not cleaned_city:
            msg = _("Pole jest wymagane.")
            self.errors["city"] = self.error_class([msg])

        if not cleaned_education:
            msg = _("Pole jest wymagane.")
            self.errors["education"] = self.error_class([msg])

        if not cleaned_physical_health:
            msg = _("Pole jest wymagane.")
            self.errors["physical_health"] = self.error_class([msg])

        if not cleaned_mental_health:
            msg = _("Pole jest wymagane.")
            self.errors["mental_health"] = self.error_class([msg])


class VolunteerBatchForm(forms.ModelForm):
    class Meta:
        model = BatchVolunteer
        fields = ['batch']
        labels = {
            'batch': _('Turnus'),
        }


class VolunteerEventForm(forms.ModelForm):
    class Meta:
        model = EventVolunteer
        fields = ['event', 'total_cost']
        labels = {
            'event': _('Wydarzenie'),
            'total_cost': _('Koszt'),
        }


class UserPasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['password', 'password_confirmation']
        labels = {
            'username': _('Nazwa użytkownika'),
            'password': _('Hasło'),
        }


class BatchTasksForm(forms.ModelForm):
    class Meta:
        model = BatchVolunteer
        fields = ['daily_activities', 'free_time_organise', 'sport_activities', 'games_organise', 'walking_trips',
                  'physical_activities', 'games_mobilisation', 'night_shift', 'kitchen_cleaning', 'general_cleaning',
                  'music_classes', 'photographing', 'funpage', 'savoir_vivre', 'care_training']
        labels = {
            'daily_activities': _('pomoc w czynnościach codziennych, tj. pomoc w ubieraniu się, jedzeniu, myciu, '
                                  'poruszaniu się'),
            'free_time_organise': _('organizacja czasu wolnego podopiecznym i wolontariuszom'),
            'sport_activities': _('zajęcia sportowo – rekreacyjne dla wszystkich uczestników wyjazdu'),
            'games_organise': _('organizowanie i prowadzenie gier, zabaw, konkursów w terenie jak i w budynku ośrodka'),
            'walking_trips': _('wycieczki piesze po okolicy'),
            'physical_activities': _('udział w zajęciach ruchowych, integracyjnych, orientacyjnych w obszarze '
                                     'wolontariusz-podopieczny'),
            'games_mobilisation': _('aktywizowanie podopiecznych przez włączanie ich do zabaw ruchowych i '
                                    'intelektualnych'),
            'night_shift': _('nocny dyżur w celu opiekuńczo-kontrolnym wszystkich podopiecznych'),
            'kitchen_cleaning': _('pomoc w pracach kuchennych, utrzymaniu czystości stołówki'),
            'general_cleaning': _('dbanie o czystość na terenie ośrodka (pokoje podopiecznych, łazienki, korytarze)'),
            'music_classes': _('prowadzenie spotkań umuzykalniających'),
            'photographing': _('tworzenie fotoreportażu podczas turnusu'),
            'funpage': _('uaktualnianie strony internetowej, fanpage\'a na Facebook\'u itp.'),
            'savoir_vivre': _('udział w szkoleniu wolontariuszy z zakresu savoir-vivre z niepełnosprawnymi'),
            'care_training': _('udział w szkoleniu wolontariuszy z zakresu pielęgnacji osób niepełnosprawnych i '
                               'starszych'),
        }


class MusicTrainingSignForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['retreat_or_music_training', 'how_know_training', 'voice', 'experience', 'instrument',
                  'accommodation', 'saturday_sunday', 'description', 'data_processing_agreement',
                  'photographing_agreement', 'total_cost']
        labels = {
            'retreat_or_music_training': _('Warsztaty'),
            'description': _('Dodatkowe informacje'),
            'how_know_training': _('Skąd dowiedziałeś/aś się o warsztatach?'),
            'voice': _('Głos'),
            'experience': _('Doświadczenie sceniczne'),
            'instrument': _('Instrument'),
            'accommodation': _('Opcja noclegu'),
            'saturday_sunday': _('Dodatkowy nocleg po wydarzeniu'),
            'data_processing_agreement': _('Wyrażam zgodę na przetwarzanie moich danych osobowych'),
            'photographing_agreement': _('Wyrażam zgodę na fotografowanie i przetwarzanie wizerunku'),
            'total_cost': _('Koszt'),
        }

    def clean(self):
        cleaned_data = super(MusicTrainingSignForm, self).clean()
        cleaned_how_know_training = cleaned_data.get('how_know_training')
        cleaned_voice = cleaned_data.get('voice')
        cleaned_experience = cleaned_data.get('experience')
        cleaned_data_processing_agreement = cleaned_data.get('data_processing_agreement')

        if not cleaned_how_know_training:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_training"] = self.error_class([msg])

        if not cleaned_voice:
            msg = _("Pole jest wymagane.")
            self.errors["voice"] = self.error_class([msg])

        if not cleaned_experience:
            msg = _("Pole jest wymagane.")
            self.errors["experience"] = self.error_class([msg])

        if not cleaned_data_processing_agreement:
            msg = _("Pole jest wymagane.")
            self.errors["data_processing_agreement"] = self.error_class([msg])


class MusicTrainingVolunteerSignForm(forms.ModelForm):

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['retreat_or_music_training', 'how_know_training', 'voice', 'experience', 'instrument',
                  'accommodation', 'saturday_sunday', 'description', 'total_cost']
        labels = {
            'retreat_or_music_training': _('Warsztaty'),
            'description': _('Dodatkowe informacje'),
            'how_know_training': _('Skąd dowiedziałeś/aś się o warsztatach?'),
            'voice': _('Głos'),
            'experience': _('Doświadczenie sceniczne'),
            'instrument': _('Instrument'),
            'accommodation': _('Opcja noclegu'),
            'saturday_sunday': _('Dodatkowy nocleg po wydarzeniu'),
            'total_cost': _('Koszt'),
        }

    def clean(self):
        cleaned_data = super(MusicTrainingVolunteerSignForm, self).clean()
        cleaned_how_know_training = cleaned_data.get('how_know_training')
        cleaned_voice = cleaned_data.get('voice')
        cleaned_experience = cleaned_data.get('experience')

        if not cleaned_how_know_training:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_training"] = self.error_class([msg])

        if not cleaned_voice:
            msg = _("Pole jest wymagane.")
            self.errors["voice"] = self.error_class([msg])

        if not cleaned_experience:
            msg = _("Pole jest wymagane.")
            self.errors["experience"] = self.error_class([msg])


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ["first_name", 'surname', 'sex', 'pesel', 'age', 'phone_number', 'email_address', 'city']
        labels = {
            "first_name": _('Imię'),
            'surname': _('Nazwisko'),
            'sex': _('Płeć'),
            'pesel': _('PESEL'),
            'age': _('Wiek'),
            'phone_number': _('Numer telefonu'),
            'email_address': _('Adres e-mail'),
            'city': _('Miejscowość'),
        }
        help_texts = {
            'pesel': 'Będzie nam potrzebny m.in. do ubezpieczenia',
            'email_address': 'Bardzo ważne dla dalszej komunikacji'
        }

    def clean(self):
        cleaned_data = super(PersonForm, self).clean()
        cleaned_pesel = cleaned_data.get('pesel')
        cleaned_phone_number = cleaned_data.get('phone_number')
        cleaned_email_address = cleaned_data.get('email_address')
        cleaned_city = cleaned_data.get('city')

        if not re.match('^[0-9]{11}$', cleaned_pesel):
            msg = _("Nieprawidłowy PESEL.")
            self.errors["pesel"] = self.error_class([msg])

        if cleaned_phone_number:
            if not re.match('^\+?1?\d{9,15}$', cleaned_phone_number):
                msg = _("Nieprawidłowy numer telefonu.")
                self.errors["phone_number"] = self.error_class([msg])

        if "." not in str(cleaned_email_address):
            msg = _("Adres e-mail jest niepoprawny.")
            self.errors["email_address"] = self.error_class([msg])

        if not cleaned_city:
            msg = _("Pole jest wymagane.")
            self.errors["city"] = self.error_class([msg])


class ExtendedPersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ["first_name", 'surname', 'sex', 'pesel', 'age', 'address', 'zip_code', 'city', 'education',
                  'phone_number', 'email_address']
        labels = {
            "first_name": _('Imię'),
            'surname': _('Nazwisko'),
            'sex': _('Płeć'),
            'pesel': _('PESEL'),
            'age': _('Wiek'),
            'address': _('Adres'),
            'zip_code': _('Kod pocztowy'),
            'city': _('Miejscowość'),
            'education': _('Wykształcenie'),
            'phone_number': _('Numer telefonu'),
            'email_address': _('Adres e-mail'),
        }
        help_texts = {
            'pesel': 'Będzie nam potrzebny m.in. do ubezpieczenia',
            'email_address': 'Bardzo ważne dla dalszej komunikacji'
        }

    def clean(self):
        cleaned_data = super(ExtendedPersonForm, self).clean()
        cleaned_pesel = cleaned_data.get('pesel')
        cleaned_phone_number = cleaned_data.get('phone_number')
        cleaned_guardian_phone_number = cleaned_data.get('guardian_phone_number')
        cleaned_email_address = cleaned_data.get('email_address')
        cleaned_address = cleaned_data.get('address')
        cleaned_zip_code = cleaned_data.get('zip_code')
        cleaned_city = cleaned_data.get('city')
        cleaned_education = cleaned_data.get('education')

        if not re.match('^[0-9]{11}$', cleaned_pesel):
            msg = _("Nieprawidłowy PESEL.")
            self.errors["pesel"] = self.error_class([msg])

        if cleaned_phone_number:
            if not re.match('^\+?1?\d{9,15}$', cleaned_phone_number):
                msg = _("Nieprawidłowy numer telefonu.")
                self.errors["phone_number"] = self.error_class([msg])

        if cleaned_guardian_phone_number:
            if not re.match('^\+?1?\d{9,15}$', cleaned_guardian_phone_number):
                msg = _("Nieprawidłowy numer telefonu.")
                self.errors["guardian_phone_number"] = self.error_class([msg])

        if "." not in str(cleaned_email_address):
            msg = _("Adres e-mail jest niepoprawny.")
            self.errors["email_address"] = self.error_class([msg])

        if cleaned_address:
            if not re.match('^(\w|[ .-])+ [1-9][0-9]*[a-zA-Z]?(/[1-9][0-9]*)?$', cleaned_address):
                msg = _("Adres jest niepoprawny.")
                self.errors["address"] = self.error_class([msg])
        else:
            msg = _("Pole jest wymagane.")
            self.errors["address"] = self.error_class([msg])

        if cleaned_zip_code:
            if not re.match('^[0-9]{2}[-][0-9]{3}$', cleaned_zip_code):
                msg = _("Kod pocztowy jest niepoprawny.")
                self.errors["zip_code"] = self.error_class([msg])
        else:
            msg = _("Pole jest wymagane.")
            self.errors["zip_code"] = self.error_class([msg])

        if not cleaned_city:
            msg = _("Pole jest wymagane.")
            self.errors["city"] = self.error_class([msg])

        if not cleaned_education:
            msg = _("Pole jest wymagane.")
            self.errors["education"] = self.error_class([msg])


class RetreatSignForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['retreat_or_music_training', 'how_know_dj', 'how_know_training', 'is_first_time', 'study', 'work',
                  'babysitting', 'pensioner', 'unemployed', 'another_work', 'guardian_phone_number', 'communion',
                  'communion_description', 'sing_or_play', 'description_why', 'accommodation',
                  'data_processing_agreement', 'photographing_agreement', 'total_cost']
        labels = {
            'retreat_or_music_training': _('Rekolekcje'),
            'how_know_dj': _('Skąd dowiedziałeś/aś się o Drabinie Jakubowej?'),
            'how_know_training': _('Skąd dowiedziałeś/aś się o rekolekcjach Drabiny Jakubowej?'),
            'is_first_time': _('Czy to twój pierwszy raz na turnusach rekolekcyjnych Drabiny Jakubowej?'),
            'study': _('Uczę się'),
            'work': _('Pracuję'),
            'babysitting': _('Opiekuję się dziećmi'),
            'pensioner': _('Jestem rencistą, emerytem'),
            'unemployed': _('Jestem bezrobotny/a'),
            'another_work': _('Inne zajęcie'),
            'guardian_phone_number': _('Numer telefonu osoby, którą będziemy mogli powiadomić w przypadku Twoich '
                                       'problemów ze zdrowiem'),
            'communion': _('Czy należysz już do duszpasterstwa Drabiny Jakubowej, Anielskiej Domówki lub innego '
                           'duszpasterstwa?'),
            'communion_description': _('Opisz, gdzie należysz i jak się angażujesz'),
            'sing_or_play': _('Gram lub śpiewam'),
            'description_why':  _('Kilka słów o sobie'),
            'accommodation': _('Opcja noclegu'),
            'data_processing_agreement': _('Wyrażam zgodę na przetwarzanie moich danych osobowych'),
            'photographing_agreement': _('Wyrażam zgodę na fotografowanie i przetwarzanie wizerunku'),
            'total_cost': _('Koszt'),
        }

    def clean(self):
        cleaned_data = super(RetreatSignForm, self).clean()
        cleaned_how_know_dj = cleaned_data.get('how_know_dj')
        cleaned_guardian_phone_number = cleaned_data.get('guardian_phone_number')
        cleaned_data_processing_agreement = cleaned_data.get('data_processing_agreement')
        cleaned_how_know_training = cleaned_data.get('how_know_training')

        if not cleaned_how_know_training:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_training"] = self.error_class([msg])

        if not cleaned_how_know_dj:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_dj"] = self.error_class([msg])

        if not cleaned_guardian_phone_number:
            msg = _("Pole jest wymagane.")
            self.errors["guardian_phone_number"] = self.error_class([msg])

        if not cleaned_data_processing_agreement:
            msg = _("Pole jest wymagane.")
            self.errors["data_processing_agreement"] = self.error_class([msg])


class RetreatVolunteerSignForm(forms.ModelForm):

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['retreat_or_music_training', 'how_know_training', 'is_first_time', 'communion',
                  'communion_description', 'description_why', 'accommodation', 'total_cost']
        labels = {
            'retreat_or_music_training': _('Rekolekcje'),
            'how_know_training': _('Skąd dowiedziałeś/aś się o rekolekcjach Drabiny Jakubowej?'),
            'is_first_time': _('Czy to twój pierwszy raz na turnusach rekolekcyjnych Drabiny Jakubowej?'),
            'communion': _('Czy należysz już do duszpasterstwa Drabiny Jakubowej, Anielskiej Domówki lub innego '
                           'duszpasterstwa?'),
            'communion_description': _('Opisz, gdzie należysz i jak się angażujesz'),
            'description_why':  _('Kilka słów o sobie'),
            'accommodation': _('Opcja noclegu'),
            'total_cost': _('Koszt'),
        }

    def clean(self):
        cleaned_data = super(RetreatVolunteerSignForm, self).clean()
        cleaned_how_know_training = cleaned_data.get('how_know_training')

        if not cleaned_how_know_training:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_training"] = self.error_class([msg])


class WorkshopSignForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['retreat_or_music_training', 'how_know_dj', 'how_know_training', 'is_first_time', 'study', 'work',
                  'babysitting', 'pensioner', 'unemployed', 'another_work', 'guardian_phone_number', 'communion',
                  'communion_description', 'sing_or_play', 'description_why', 'accommodation',
                  'data_processing_agreement', 'photographing_agreement', 'total_cost']
        labels = {
            'retreat_or_music_training': _('Warsztaty'),
            'how_know_dj': _('Skąd dowiedziałeś/aś się o Drabinie Jakubowej?'),
            'how_know_training': _('Skąd dowiedziałeś/aś się o warsztatach Drabiny Jakubowej?'),
            'is_first_time': _('Czy to twój pierwszy raz na warsztatach Drabiny Jakubowej?'),
            'study': _('Uczę się'),
            'work': _('Pracuję'),
            'babysitting': _('Opiekuję się dziećmi'),
            'pensioner': _('Jestem rencistą, emerytem'),
            'unemployed': _('Jestem bezrobotny/a'),
            'another_work': _('Inne zajęcie'),
            'guardian_phone_number': _('Numer telefonu osoby, którą będziemy mogli powiadomić w przypadku Twoich '
                                       'problemów ze zdrowiem'),
            'communion': _('Czy należysz już do duszpasterstwa Drabiny Jakubowej, Anielskiej Domówki lub innego '
                           'duszpasterstwa?'),
            'communion_description': _('Opisz, gdzie należysz i jak się angażujesz'),
            'sing_or_play': _('Gram lub śpiewam'),
            'description_why':  _('Kilka słów o sobie'),
            'accommodation': _('Opcja noclegu'),
            'data_processing_agreement': _('Wyrażam zgodę na przetwarzanie moich danych osobowych'),
            'photographing_agreement': _('Wyrażam zgodę na fotografowanie i przetwarzanie wizerunku'),
            'total_cost': _('Koszt'),
        }

    def clean(self):
        cleaned_data = super(WorkshopSignForm, self).clean()
        cleaned_how_know_dj = cleaned_data.get('how_know_dj')
        cleaned_guardian_phone_number = cleaned_data.get('guardian_phone_number')
        cleaned_data_processing_agreement = cleaned_data.get('data_processing_agreement')
        cleaned_how_know_training = cleaned_data.get('how_know_training')

        if not cleaned_how_know_training:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_training"] = self.error_class([msg])

        if not cleaned_how_know_dj:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_dj"] = self.error_class([msg])

        if not cleaned_guardian_phone_number:
            msg = _("Pole jest wymagane.")
            self.errors["guardian_phone_number"] = self.error_class([msg])

        if not cleaned_data_processing_agreement:
            msg = _("Pole jest wymagane.")
            self.errors["data_processing_agreement"] = self.error_class([msg])


class WorkshopVolunteerSignForm(forms.ModelForm):

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['retreat_or_music_training', 'how_know_training', 'is_first_time', 'communion',
                  'communion_description', 'description_why', 'accommodation', 'total_cost']
        labels = {
            'retreat_or_music_training': _('Warsztaty'),
            'how_know_training': _('Skąd dowiedziałeś/aś się o warsztatach Drabiny Jakubowej?'),
            'is_first_time': _('Czy to twój pierwszy raz na warsztatach Drabiny Jakubowej?'),
            'communion': _('Czy należysz już do duszpasterstwa Drabiny Jakubowej, Anielskiej Domówki lub innego '
                           'duszpasterstwa?'),
            'communion_description': _('Opisz, gdzie należysz i jak się angażujesz'),
            'description_why': _('Kilka słów o sobie'),
            'accommodation': _('Opcja noclegu'),
            'total_cost': _('Koszt'),
        }

    def clean(self):
        cleaned_data = super(WorkshopVolunteerSignForm, self).clean()
        cleaned_how_know_training = cleaned_data.get('how_know_training')

        if not cleaned_how_know_training:
            msg = _("Pole jest wymagane.")
            self.errors["how_know_training"] = self.error_class([msg])


class UserRemindPasswordForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email']
        labels = {
            'email': _('Adres e-mail'),
        }

    def clean(self):
        cleaned_data = super(UserRemindPasswordForm, self).clean()
        cleaned_email = cleaned_data.get('email')

        if cleaned_email is None:
            msg = _("Pole jest wymagane.")
            self.errors["email"] = self.error_class([msg])
