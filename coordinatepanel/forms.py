from django import forms
from .models import *
from dj.models import File
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
import pytz

utc = pytz.UTC

now = datetime.now()


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


class SetRoomForm(forms.ModelForm):

    class Meta:
        model = BatchVolunteer
        fields = ['room']
        labels = {
            'room': _('Pokój'),
        }


class BatchVolunteerForm(forms.ModelForm):

    class Meta:
        model = BatchVolunteer
        fields = ['room', 'batch_begin_date', 'batch_end_date', 'participant_helper', 'nights', 'was_there', 'note']
        labels = {
            'room': _('Pokój'),
            'batch_begin_date': _('Data przyjazdu na turnus'),
            'batch_end_date': _('Data opuszczenia turnusu'),
            'participant_helper': _('Pomoc przy podopiecznych'),
            'nights': _('Dyżury nocne'),
            'was_there': _('Odbył turnus'),
            'note': _('Notatka'),
        }

    def clean(self):
        cleaned_data = super(BatchVolunteerForm, self).clean()
        today = now.replace(tzinfo=utc)
        cleaned_begin_date = cleaned_data.get('batch_begin_date')
        cleaned_end_date = cleaned_data.get('batch_end_date')
        cleaned_nights = cleaned_data.get('nights')

        if cleaned_begin_date:
            cleaned_begin_date = cleaned_begin_date.replace(tzinfo=utc)
            if cleaned_end_date:
                cleaned_end_date = cleaned_end_date.replace(tzinfo=utc)
                if cleaned_begin_date.date() >= cleaned_end_date.date():
                    msg = _("Data końcowa musi być większa niż początkowa.")
                    self.add_error('batch_end_date', msg)
            else:
                msg = _("Nieprawidłowa data.")
                self.errors["batch_end_date"] = self.error_class([msg])
        else:
            msg = _("Nieprawidłowa data.")
            self.errors["batch_begin_date"] = self.error_class([msg])
        if not cleaned_end_date:
            msg = _("Nieprawidłowa data.")
            self.errors["batch_end_date"] = self.error_class([msg])

        if cleaned_nights < 0:
            msg = _("Liczba nie może być mniejsza od 0.")
            self.errors["nights"] = self.error_class([msg])


class BatchParticipantForm(forms.ModelForm):

    class Meta:
        model = BatchParticipant
        fields = ['room', 'volunteer', 'batch_begin_date', 'batch_end_date', 'note']
        labels = {
            'room': _('Pokój'),
            'volunteer': _('Wolontariusz'),
            'batch_begin_date': _('Data przyjazdu na turnus'),
            'batch_end_date': _('Data opuszczenia turnusu'),
            'note': _('Notatka'),
        }

    def clean(self):
        cleaned_data = super(BatchParticipantForm, self).clean()
        cleaned_begin_date = cleaned_data.get('batch_begin_date')
        cleaned_end_date = cleaned_data.get('batch_end_date')
        if cleaned_begin_date:
            cleaned_begin_date = cleaned_begin_date.replace(tzinfo=utc)
            if cleaned_end_date:
                cleaned_end_date = cleaned_end_date.replace(tzinfo=utc)
                if cleaned_begin_date.date() >= cleaned_end_date.date():
                    msg = _("Data końcowa musi być większa niż początkowa.")
                    self.add_error('batch_end_date', msg)
            else:
                msg = _("Nieprawidłowa data.")
                self.errors["batch_end_date"] = self.error_class([msg])
        else:
            msg = _("Nieprawidłowa data.")
            self.errors["batch_begin_date"] = self.error_class([msg])
        if not cleaned_end_date:
            msg = _("Nieprawidłowa data.")
            self.errors["batch_end_date"] = self.error_class([msg])


class RetreatOrMusicTrainingPersonForm(forms.ModelForm):

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['room']
        labels = {
            'room': _('Pokój'),
        }


class PersonPaymentForm(forms.ModelForm):

    class Meta:
        model = RetreatOrMusicTrainingPerson
        fields = ['total_cost', 'is_paid']
        labels = {
            'total_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
        }


class EventVolunteerPaymentForm(forms.ModelForm):

    class Meta:
        model = EventVolunteer
        fields = ['total_cost', 'is_paid']
        labels = {
            'total_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
        }


class EventParticipantPaymentForm(forms.ModelForm):

    class Meta:
        model = EventParticipant
        fields = ['total_cost', 'is_paid']
        labels = {
            'total_cost': _('Pełna kwota'),
            'is_paid': _('Całość zapłacona'),
        }


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


class UploadFileForm(forms.ModelForm):

    class Meta:
        model = File
        fields = ['title', 'upload']
        labels = {
            'title': _('Nazwa'),
            'upload': _('Plik'),
        }

    def clean(self):
        cleaned_data = super(UploadFileForm, self).clean()
        upload = cleaned_data.get('upload')
        if upload:
            if upload.size > 1024 * 1024 * 5:
                msg = _("Plik jest za duży (max. 5 MB).")
                self.errors["upload"] = self.error_class([msg])


class EventInformationForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['info']
        labels = {
            'info': _('Informacje'),
        }


class EventParticipantForm(forms.ModelForm):

    class Meta:
        model = EventParticipant
        fields = ['volunteer']
        labels = {
            'volunteer': _('Wolontariusz'),
        }


class ParticipantForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ['is_first_time']
        labels = {
            'is_first_time': _('Pierwszy raz na DJ'),
        }
