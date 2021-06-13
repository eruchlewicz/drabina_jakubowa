from django import forms
from coordinatepanel.models import *
from dj.models import *
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import pytz
import re

utc = pytz.UTC

now = datetime.now()


class BatchParticipantForm(forms.ModelForm):

    class Meta:
        model = BatchParticipant
        fields = ['batch', 'reserve_list']
        labels = {
            'batch': _('Turnus'),
            'reserve_list': _('Lista rezerwowa'),
        }


class ParticipantForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ["first_name", 'surname', 'sex', 'pesel', 'phone_number', 'guardian_name', 'guardian_phone_number',
                  'email_address', 'city', 'zip_code', 'address', 'is_first_time', 'how_know_dj', 'foundation',
                  'candies', 'flower', "cat", "dog", "bear", "monkey",
                  "frog", "bat", "spider", "fish", 'others']
        labels = {
            "first_name": _('Imię'),
            'surname': _('Nazwisko'),
            'sex': _('Płeć'),
            'pesel': _('PESEL'),
            'phone_number': _('Numer telefonu'),
            'guardian_name': _('Imię i nazwisko opiekuna'),
            'guardian_phone_number': _('Numer telefonu opiekuna'),
            'email_address': _('Adres e-mail'),
            'city': _('Miejscowość'),
            'zip_code': _('Kod pocztowy'),
            'address': _('Adres zamieszkania'),
            'is_first_time': _('Pierwszy raz'),
            'how_know_dj': _('Skąd zna DJ?'),
            'foundation': _('Dane fundacji np. do wystawienia zaświadczenia'),
            'candies': _('Czy przyjmuje leki?'),
            'flower': _('Komunikacja'),
            "cat": _('Niepełnosprawność intelektualna'),
            "dog": _('Nie potrzebuje pomocy przy codziennych czynnościach'),
            "bear": _('Porusza się na wózku'),
            "monkey": _('Niesprawne ręce'),
            "frog": _('Porusza się o kulach'),
            "bat": _('Niesprawny wzrok'),
            "spider": _('Niesprawny słuch'),
            "fish": _('Możliwe ataki padaczki'),
            'others': _('Uwagi'),
        }

    def clean(self):
        cleaned_data = super(ParticipantForm, self).clean()
        cleaned_pesel = cleaned_data.get('pesel')
        cleaned_phone_number = cleaned_data.get('phone_number')
        cleaned_email_address = cleaned_data.get('email_address')
        cleaned_guardian_phone_number = cleaned_data.get('guardian_phone_number')
        cleaned_address = cleaned_data.get('address')
        cleaned_zip_code = cleaned_data.get('zip_code')

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

        if cleaned_guardian_phone_number:
            if not re.match('^\+?1?\d{9,15}$', cleaned_guardian_phone_number):
                msg = _("Nieprawidłowy numer telefonu.")
                self.errors["guardian_phone_number"] = self.error_class([msg])

        if cleaned_email_address:
            if "." not in str(cleaned_email_address):
                msg = _("Adres e-mail jest niepoprawny.")
                self.errors["email_address"] = self.error_class([msg])

        if not re.match('^(\w|[ .-])+([a-zA-Z])?([0-9])+([a-zA-Z])?(/[a-zA-Z]?[0-9]+[a-zA-Z]?)?$', cleaned_address):
            msg = _("Adres jest niepoprawny.")
            self.errors["address"] = self.error_class([msg])

        if not re.match('^[0-9]{2}[-][0-9]{3}$', cleaned_zip_code):
            msg = _("Kod pocztowy jest niepoprawny.")
            self.errors["zip_code"] = self.error_class([msg])


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ["first_name", 'surname', 'phone_number', 'email_address', 'begin_date', 'end_date']
        labels = {
            "first_name": _('Imię'),
            'surname': _('Nazwisko'),
            'phone_number': _('Numer telefonu'),
            'email_address': _('Adres email'),
            'begin_date': _('Początek pobytu'),
            'end_date': _('Koniec pobytu'),
        }

    def clean(self):
        cleaned_data = super(BookingForm, self).clean()
        today = now.replace(tzinfo=utc)
        cleaned_begin_date = cleaned_data.get('begin_date')
        cleaned_end_date = cleaned_data.get('end_date')
        if cleaned_begin_date:
            cleaned_begin_date = cleaned_begin_date.replace(tzinfo=utc)
            if cleaned_begin_date < today:
                msg = _("Ten dzień już minął.")
                self.add_error('begin_date', msg)
            if cleaned_end_date:
                cleaned_end_date = cleaned_end_date.replace(tzinfo=utc)
                if cleaned_begin_date.date() >= cleaned_end_date.date():
                    msg = _("Data końcowa musi być większa niż początkowa.")
                    self.add_error('end_date', msg)
            else:
                msg = _("Nieprawidłowa data.")
                self.errors["end_date"] = self.error_class([msg])
        else:
            msg = _("Nieprawidłowa data.")
            self.errors["begin_date"] = self.error_class([msg])
        if not cleaned_end_date:
            msg = _("Nieprawidłowa data.")
            self.errors["end_date"] = self.error_class([msg])

        cleaned_email_address = cleaned_data.get('email_address')

        if "." not in str(cleaned_email_address):
            msg = _("Adres e-mail jest niepoprawny.")
            self.errors["email_address"] = self.error_class([msg])


class BookingRoomForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['begin_date', 'end_date', 'room', 'adults',
                  'kids', 'full_cost', 'meals', 'who_where']
        labels = {
            'room': _('Pokoje'),
            'begin_date': _('Początek pobytu'),
            'end_date': _('Koniec pobytu'),
            'adults': _('Dorośli i młodzież'),
            'kids': _('Dzieci (2-11)'),
            'full_cost': _('Finalna cena'),
            'meals': _('Posiłki?'),
            'who_where': _('Kto gdzie?'),
        }

    def clean(self):
        cleaned_data = super(BookingRoomForm, self).clean()
        cleaned_adults = cleaned_data.get('adults')
        cleaned_kids = cleaned_data.get('kids')

        if cleaned_adults < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["adults"] = self.error_class([msg])

        if cleaned_kids < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["kids"] = self.error_class([msg])


class BookingMealsForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ["first_name", 'surname', 'phone_number', 'email_address', 'begin_date', 'end_date', 'adults',
                  'kids', 'full_cost']
        labels = {
            "first_name": _('Imię'),
            'surname': _('Nazwisko'),
            'phone_number': _('Numer telefonu'),
            'email_address': _('Adres email'),
            'begin_date': _('Początek pobytu'),
            'end_date': _('Koniec pobytu'),
            'adults': _('Dorośli i młodzież'),
            'kids': _('Dzieci (2-11)'),
            'full_cost': _('Finalna cena'),
        }

    def clean(self):
        cleaned_data = super(BookingMealsForm, self).clean()
        today = now.replace(tzinfo=utc)
        cleaned_begin_date = cleaned_data.get('begin_date')
        cleaned_end_date = cleaned_data.get('end_date')
        if cleaned_begin_date:
            cleaned_begin_date = cleaned_begin_date.replace(tzinfo=utc)
            if cleaned_begin_date < today:
                msg = _("Ten dzień już minął.")
                self.add_error('begin_date', msg)
            if cleaned_end_date:
                cleaned_end_date = cleaned_end_date.replace(tzinfo=utc)
                if cleaned_begin_date.date() >= cleaned_end_date.date():
                    msg = _("Data końcowa musi być większa niż początkowa.")
                    self.add_error('end_date', msg)
            else:
                msg = _("Nieprawidłowa data.")
                self.errors["end_date"] = self.error_class([msg])
        else:
            msg = _("Nieprawidłowa data.")
            self.errors["begin_date"] = self.error_class([msg])
        if not cleaned_end_date:
            msg = _("Nieprawidłowa data.")
            self.errors["end_date"] = self.error_class([msg])

        cleaned_email_address = cleaned_data.get('email_address')

        if "." not in str(cleaned_email_address):
            msg = _("Adres e-mail jest niepoprawny.")
            self.errors["email_address"] = self.error_class([msg])

        cleaned_adults = cleaned_data.get('adults')
        cleaned_kids = cleaned_data.get('kids')

        if cleaned_adults <= 0:
            msg = _("Liczba musi być większa od 0.")
            self.errors["adults"] = self.error_class([msg])

        if cleaned_kids < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["kids"] = self.error_class([msg])


class PaymentForm(forms.ModelForm):

    class Meta:
        model = BatchParticipant
        fields = ['installment', 'is_part_paid', 'full_cost', 'is_paid', 'payment_method']
        labels = {
            'installment': _('Zaliczka'),
            'is_part_paid': _('Zaliczka zapłacona'),
            'full_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
            'payment_method': _('Metoda płatności'),
        }

    def clean(self):
        cleaned_data = super(PaymentForm, self).clean()
        cleaned_full_cost = cleaned_data.get('full_cost')
        cleaned_installment = cleaned_data.get('installment')

        if cleaned_full_cost < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["full_cost"] = self.error_class([msg])

        if cleaned_installment < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["installment"] = self.error_class([msg])


class BookingPaymentForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['installment', 'is_part_paid', 'full_cost', 'is_paid']
        labels = {
            'installment': _('Zaliczka'),
            'is_part_paid': _('Zaliczka zapłacona'),
            'full_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
        }

    def clean(self):
        cleaned_data = super(BookingPaymentForm, self).clean()
        cleaned_full_cost = cleaned_data.get('full_cost')
        cleaned_installment = cleaned_data.get('installment')

        if cleaned_full_cost < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["full_cost"] = self.error_class([msg])

        if cleaned_installment < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["installment"] = self.error_class([msg])


class EventParticipantForm(forms.ModelForm):

    class Meta:
        model = EventParticipant
        fields = ['event']
        labels = {
            'event': _('Wydarzenie'),
        }


class PersonPaymentForm(forms.ModelForm):

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['total_cost', 'is_paid']
        labels = {
            'total_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
        }

    def clean(self):
        cleaned_data = super(PersonPaymentForm, self).clean()
        cleaned_total_cost = cleaned_data.get('total_cost')

        if cleaned_total_cost < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["total_cost"] = self.error_class([msg])


class EventVolunteerPaymentForm(forms.ModelForm):

    class Meta:
        model = EventVolunteer
        fields = ['total_cost', 'is_paid']
        labels = {
            'total_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
        }

    def clean(self):
        cleaned_data = super(EventVolunteerPaymentForm, self).clean()
        cleaned_total_cost = cleaned_data.get('total_cost')

        if cleaned_total_cost < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["total_cost"] = self.error_class([msg])


class EventParticipantPaymentForm(forms.ModelForm):

    class Meta:
        model = EventParticipant
        fields = ['total_cost', 'is_paid']
        labels = {
            'total_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
        }

    def clean(self):
        cleaned_data = super(EventParticipantPaymentForm, self).clean()
        cleaned_total_cost = cleaned_data.get('total_cost')

        if cleaned_total_cost < 0:
            msg = _("Liczba musi być większa lub równa 0.")
            self.errors["total_cost"] = self.error_class([msg])


class SetParticipantPhotoForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['photo']
        labels = {
            'photo': _('Zdjęcie'),
        }

    def clean(self):
        cleaned_data = super(SetParticipantPhotoForm, self).clean()
        photo = cleaned_data.get('photo')
        if photo:
            if photo.size > 1024 * 1024 / 2:
                msg = _("Plik jest za duży (max. 500 KB).")
                self.errors["photo"] = self.error_class([msg])
