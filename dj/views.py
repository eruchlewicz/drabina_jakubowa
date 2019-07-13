from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View, DetailView
from .models import *
from .forms import *
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import Group
import logging
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from easy_pdf.views import PDFTemplateResponseMixin
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
import smtplib
from django.conf import settings
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string

now = timezone.now()
logger = logging.getLogger(__name__)


def index(request):
    batches = Batch.objects.filter(begin_date__year=now.year).order_by('begin_date') | \
              Batch.objects.filter(begin_date__year=now.year+1).order_by('begin_date')
    batches_participant = Batch.objects.filter(begin_date__year=now.year).order_by('begin_date') | \
        Batch.objects.filter(begin_date__year=now.year+1).order_by('begin_date')
    for b in batches_participant:
        if not b.name == "Sylwester":
            b.begin_date = b.begin_date + timedelta(2)
    prices = Price.objects.all()
    cities = (Batch.objects.filter(begin_date__year=now.year).values('institution__city') |
              Batch.objects.filter(begin_date__year=now.year+1).values('institution__city')).distinct()
    return render(request, 'dj/home.html', {'now': now, 'batches': batches, 'cities': cities,
                                            'batches_participant': batches_participant, 'prices': prices})


def news_view(request):
    posts_list = Post.objects.all().order_by('-date')
    return render(request, 'dj/news.html', {'post_list': posts_list})


def costs_view(request):
    price_b = Price.objects.filter(service='Brańszczyk').first()
    price_k = Price.objects.filter(service='Kalisz').first()
    return render(request, 'dj/costs.html', {'price_b': price_b, 'price_k': price_k})


class UserFormView(View):
    form_class = UserForm
    form_class_2 = VolunteerForm
    form_class_3 = VolunteerBatchForm
    template_name = 'dj/registration.html'

    # display blank form
    def get(self, request):
        user_form = self.form_class(None)
        user_form.fields['password'].label = "Hasło"
        user_form.fields['password_confirmation'].label = "Powtórz hasło"
        volunteer_form = self.form_class_2(None)
        volunteer_batch_form = self.form_class_3(None)
        volunteer_batch_form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year,
                                                                              begin_date__gte=now) |
                                                         Batch.objects.filter(begin_date__year=now.year+1,
                                                                              begin_date__gte=now))\
            .order_by('begin_date')

        return render(request, self.template_name, {'user_form': user_form, 'volunteer_form': volunteer_form,
                                                    'volunteer_batch_form': volunteer_batch_form})

    # process form data
    def post(self, request):
        user_form = self.form_class(request.POST)
        volunteer_form = self.form_class_2(request.POST)
        volunteer_batch_form = self.form_class_3(request.POST)

        if user_form.is_valid() and volunteer_form.is_valid() and volunteer_batch_form.is_valid():

            # cleaned (normalized) data
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            password_confirmation = user_form.cleaned_data['password_confirmation']
            email = user_form.cleaned_data['email']
            first_name = user_form.cleaned_data['first_name']
            last_name = user_form.cleaned_data['last_name']
            data_processing_agreement = volunteer_form.cleaned_data['data_processing_agreement']
            batch = volunteer_batch_form.cleaned_data['batch']

            if password == password_confirmation and data_processing_agreement is True:
                user = user_form.save(commit=False)
                user.set_password(password)
                user.save()
                volunteer = volunteer_form.save(commit=False)
                volunteer.email_address = email
                volunteer.user = user
                volunteer.first_name = first_name
                volunteer.surname = last_name
                volunteer.save()
                if batch is not None:
                    volunteer_batch = volunteer_batch_form.save(commit=False)
                    volunteer_batch.volunteer = volunteer
                    volunteer_batch.batch_begin_date = batch.begin_date
                    volunteer_batch.batch_end_date = batch.end_date
                    volunteer_batch.batch_days = abs(batch.end_date - batch.begin_date).days - 1
                    volunteer_batch.save()
                    batch.volunteers += 1
                    batch.save()

                group = Group.objects.get_or_create(name='Wolontariusze')
                group = Group.objects.get(name="Wolontariusze")
                group_id = group.id
                user.groups.add(group_id)

                user = authenticate(username=username, password=password)

                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('dj:batches')

        return render(request, self.template_name, {'user_form': user_form, 'volunteer_form': volunteer_form,
                                                    'volunteer_batch_form': volunteer_batch_form})


class UserEventFormView(View):
    form_class = UserForm
    form_class_2 = VolunteerForm
    form_class_4 = VolunteerEventForm
    template_name = 'dj/event_registration.html'

    # display blank form
    def get(self, request):
        if request.user.is_authenticated:
            return events_view(request)
        else:
            prices_list = Event.objects.all().values('id', 'price')
            prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
            user_form = self.form_class(None)
            user_form.fields['password'].label = "Hasło"
            user_form.fields['password_confirmation'].label = "Powtórz hasło"
            volunteer_form = self.form_class_2(None)
            volunteer_event_form = self.form_class_4(None)
            volunteer_event_form.fields["event"].queryset = (Event.objects.filter(begin_date__year=now.year,
                                                                                  begin_date__gte=now) |
                                                             Event.objects.filter(begin_date__year=now.year+1,
                                                                                  begin_date__gte=now) |
                                                             Event.objects.filter(end_date__gte=now))\
                .order_by('begin_date')

            return render(request, self.template_name, {'user_form': user_form, 'volunteer_form': volunteer_form,
                                                        'volunteer_event_form': volunteer_event_form,
                                                        'prices_json': prices_json})

    # process form data
    def post(self, request):
        if request.user.is_authenticated:
            return events_view(request)
        else:
            prices_list = Event.objects.all().values('id', 'price')
            prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
            user_form = self.form_class(request.POST)
            volunteer_form = self.form_class_2(request.POST)
            volunteer_event_form = self.form_class_4(request.POST)

            if user_form.is_valid() and volunteer_form.is_valid() and volunteer_event_form.is_valid():

                # cleaned (normalized) data
                username = user_form.cleaned_data['username']
                password = user_form.cleaned_data['password']
                password_confirmation = user_form.cleaned_data['password_confirmation']
                email = user_form.cleaned_data['email']
                first_name = user_form.cleaned_data['first_name']
                last_name = user_form.cleaned_data['last_name']
                data_processing_agreement = volunteer_form.cleaned_data['data_processing_agreement']
                event = volunteer_event_form.cleaned_data['event']

                if password == password_confirmation and data_processing_agreement is True:
                    user = user_form.save(commit=False)
                    user.set_password(password)
                    user.save()
                    volunteer = volunteer_form.save(commit=False)
                    volunteer.email_address = email
                    volunteer.user = user
                    volunteer.first_name = first_name
                    volunteer.surname = last_name
                    volunteer.save()

                    if event is not None:
                        volunteer_event = volunteer_event_form.save(commit=False)
                        volunteer_event.volunteer = volunteer
                        volunteer_event.save()
                        event.volunteers += 1
                        event.save()

                    group = Group.objects.get_or_create(name='Wolontariusze')
                    group = Group.objects.get(name="Wolontariusze")
                    group_id = group.id
                    user.groups.add(group_id)

                    user = authenticate(username=username, password=password)

                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            return redirect('dj:batches')

            return render(request, self.template_name, {'user_form': user_form, 'volunteer_form': volunteer_form,
                                                        'volunteer_event_form': volunteer_event_form,
                                                        'prices_json': prices_json})


def login_view(request):
    form_class = AuthenticationForm
    template_name = 'dj/login.html'

    if request.method == 'POST':
        form = form_class(data=request.POST)
        form.fields['password'].label = "Hasło"
        form.fields['username'].label = "Nazwa użytkownika"
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                if user.groups.filter(name='Wolontariusze').exists():
                    login(request, user)
                    return redirect('dj:batches')
    else:
        form = form_class()
        form.fields['password'].label = "Hasło"
        form.fields['username'].label = "Nazwa użytkownika"
    return render(request, template_name, {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('dj:index')


@login_required
def batches_view(request):
    form_class = VolunteerBatchForm
    template_name = 'dj/batches.html'
    volunteer = Volunteer.objects.filter(user=request.user).first()
    batches_list = BatchVolunteer.objects.filter(volunteer=volunteer).order_by('-batch_begin_date')
    coordinator = Coordinator.objects.filter(volunteer=volunteer).first()
    today = now
    form = form_class(request.POST or None)
    batches = Batch.objects.exclude(batchvol__in=batches_list)
    form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year, begin_date__gte=now,
                                                          id__in=batches) |
                                     Batch.objects.filter(begin_date__year=now.year+1, begin_date__gte=now,
                                                          id__in=batches)).distinct().order_by('begin_date')

    if request.method == 'POST':
        if form.is_valid():
            batch = form.cleaned_data['batch']
            if batch is not None:
                user_exists_in_batch = BatchVolunteer.objects.filter(batch=batch, volunteer=volunteer).count()
                any_batch = BatchVolunteer.objects.filter(volunteer=volunteer).count()
                if user_exists_in_batch == 0:
                    batch_volunteer = form.save(commit=False)
                    batch_volunteer.volunteer = volunteer
                    batch_volunteer.batch = batch
                    batch_volunteer.batch_begin_date = batch.begin_date
                    batch_volunteer.batch_end_date = batch.end_date
                    batch_volunteer.batch_days = abs(batch.end_date - batch.begin_date).days - 1
                    batch_volunteer.save()
                    form = VolunteerBatchForm(None)
                    batches = Batch.objects.exclude(batchvol__in=batches_list)
                    form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year,
                                                                          begin_date__gte=now, id__in=batches) |
                                                     Batch.objects.filter(begin_date__year=now.year+1,
                                                                          begin_date__gte=now, id__in=batches))\
                        .distinct()\
                        .order_by('begin_date')
                    batch.volunteers += 1
                    batch.save()

                    if any_batch > 0:
                        volunteer.is_first_time = False
                        volunteer.save()

                    messages.success(request, 'Zapisano na turnus.')
    else:
        form = form_class()
        batches = Batch.objects.exclude(batchvol__in=batches_list)
        form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year, begin_date__gte=now,
                                                              id__in=batches) |
                                         Batch.objects.filter(begin_date__year=now.year+1, begin_date__gte=now,
                                                              id__in=batches)).distinct().order_by('begin_date')

    return render(request, template_name, {'batches_list': batches_list, 'volunteer': volunteer, 'today': today,
                                           'coordinator': coordinator, 'form': form})


@login_required
def user_account_view(request):
    template_name = 'dj/user_account.html'
    volunteer = Volunteer.objects.filter(user=request.user).first()
    return render(request, template_name, {'user_details': volunteer})


@login_required
def user_account_edit(request):
    form_class = VolunteerEditForm
    template_name = 'dj/user_account_edit.html'
    user = request.user
    volunteer = Volunteer.objects.filter(user=user).first()
    person = Person.objects.filter(pesel=volunteer.pesel).first()
    form = form_class(request.POST or None, instance=volunteer)
    if request.POST and form.is_valid():
        form.save()
        user.email = volunteer.email_address
        user.first_name = volunteer.first_name
        user.last_name = volunteer.surname
        user.save()
        if person is not None:
            person.first_name = volunteer.first_name
            person.surname = volunteer.surname
            person.pesel = volunteer.pesel
            person.email_address = volunteer.email_address
            person.phone_number = volunteer.phone_number
            person.save()

        messages.success(request, 'Dane zostały zaktualizowane.')
        return redirect('dj:user_account')
    return render(request, template_name, {'form': form})


@login_required
def change_password(request):
    form_class = PasswordChangeForm
    template_name = 'dj/user_password.html'
    if request.method == 'POST':
        form = form_class(request.user, request.POST)
        form.fields['old_password'].label = "Bieżące hasło"
        form.fields['new_password1'].label = "Nowe hasło"
        form.fields['new_password1'].help_text = "Hasło powinno mieć min. 8 znaków, przynajmniej jedną cyfrę i znak " \
                                                 "specjalny."
        form.fields['new_password2'].label = "Powtórz nowe hasło"
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(request, 'Hasło zostało zmienione.')
            return redirect('dj:user_account')
    else:
        form = form_class(request.user)
        form.fields['old_password'].label = "Bieżące hasło"
        form.fields['new_password1'].label = "Nowe hasło"
        form.fields['new_password1'].help_text = "Hasło powinno mieć min. 8 znaków, przynajmniej jedną cyfrę i znak " \
                                                 "specjalny."
        form.fields['new_password2'].label = "Powtórz nowe hasło"
    return render(request, template_name, {'form': form})


@login_required
def batch_view(request, **kwargs):
    template_name = 'dj/batch_details.html'
    batch_details = Batch.objects.filter(id=kwargs['pk']).first()
    volunteer = Volunteer.objects.filter(user=request.user)
    batch_participants = BatchParticipant.objects.filter(batch=batch_details, volunteer=volunteer)
    batch_volunteer = BatchVolunteer.objects.filter(batch=batch_details, volunteer=volunteer).first()
    return render(request, template_name, {'batch_details': batch_details, 'batch_participants': batch_participants,
                                           'batch_volunteer': batch_volunteer, 'now': now})


@login_required
def batch_tasks_edit(request, **kwargs):
    form_class = BatchTasksForm
    template_name = 'dj/batch_tasks.html'
    volunteer = Volunteer.objects.filter(user=request.user)
    batch_volunteer = BatchVolunteer.objects.filter(volunteer=volunteer, batch=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=batch_volunteer)
    if request.POST and form.is_valid():
        form.save()

        messages.success(request, 'Zadania zostały zapisane.')
        return redirect('dj:batches')
    return render(request, template_name, {'form': form})


@login_required
def participant_details(request, **kwargs):
    participant = Participant.objects.filter(id=kwargs['participant_id']).first()
    batch = Batch.objects.filter(id=kwargs["pk"]).first()
    return render(request, 'dj/participant_details.html', {'batch_id': kwargs["pk"], 'batch': batch,
                                                           'participant': participant})


class CertificatePDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'dj/certificate/certificate.html'
    download_filename = 'certificate.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(volunteer__user=self.request.user, batch__id=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(CertificatePDFView, self).get_context_data(
            pagesize='A4',
            title='Zaświadczenie',
            congregation=Congregation.objects.first(),
            home=Home.objects.first(),
            date=datetime.now(),
            **kwargs
        )


class NurseCertificatePDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'dj/certificate/nurse_certificate.html'
    download_filename = 'certificate.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(volunteer__user=self.request.user, batch__id=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(NurseCertificatePDFView, self).get_context_data(
            pagesize='A4',
            title='Zaświadczenie',
            congregation=Congregation.objects.first(),
            home=Home.objects.first(),
            date=datetime.now(),
            **kwargs
        )


class DoctorCertificatePDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'dj/certificate/doctor_certificate.html'
    download_filename = 'certificate.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(volunteer__user=self.request.user, batch__id=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(DoctorCertificatePDFView, self).get_context_data(
            pagesize='A4',
            title='Zaświadczenie',
            congregation=Congregation.objects.first(),
            home=Home.objects.first(),
            date=datetime.now(),
            **kwargs
        )


class ContractPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'dj/contract/contract.html'
    download_filename = 'contract.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(volunteer__user=self.request.user, batch__id=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(ContractPDFView, self).get_context_data(
            pagesize='A4',
            title='Umowa',
            congregation=Congregation.objects.first(),
            date=datetime.now(),
            **kwargs
        )


class NurseContractPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'dj/contract/nurse_contract.html'
    download_filename = 'contract.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(volunteer__user=self.request.user, batch__id=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(NurseContractPDFView, self).get_context_data(
            pagesize='A4',
            title='Umowa',
            congregation=Congregation.objects.first(),
            date=datetime.now(),
            **kwargs
        )


class DoctorContractPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'dj/contract/doctor_contract.html'
    download_filename = 'contract.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(volunteer__user=self.request.user, batch__id=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(DoctorContractPDFView, self).get_context_data(
            pagesize='A4',
            title='Umowa',
            congregation=Congregation.objects.first(),
            date=datetime.now(),
            **kwargs
        )


def bad_request(request):
    return render(request, 'dj/400.html')


def permission_denied(request):
    return render(request, 'dj/403.html')


def page_not_found(request):
    return render(request, 'dj/404.html')


def server_error(request):
    return render(request, 'dj/500.html')


@login_required
def events_view(request):
    prices_list = Event.objects.all().values('id', 'price')
    prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
    form_class = VolunteerEventForm
    template_name = 'dj/events.html'
    volunteer = Volunteer.objects.filter(user=request.user).first()
    vol_events_list = EventVolunteer.objects.filter(volunteer=volunteer).order_by('-event__begin_date')
    form = form_class(request.POST or None)
    events = Event.objects.exclude(evvol__in=vol_events_list)
    form.fields["event"].queryset = (Event.objects.filter(begin_date__year=now.year, begin_date__gte=now,
                                                          id__in=events) |
                                     Event.objects.filter(begin_date__year=now.year+1, begin_date__gte=now,
                                                          id__in=events) |
                                     Event.objects.filter(end_date__gte=now, id__in=events))\
        .distinct()\
        .order_by('begin_date')
    if request.method == 'POST':
        if form.is_valid():
            event = form.cleaned_data['event']
            user_exists_in_event = EventVolunteer.objects.filter(event=event, volunteer=volunteer).count()
            if user_exists_in_event == 0:
                event_volunteer = form.save(commit=False)
                event_volunteer.volunteer = volunteer
                event_volunteer.event = event
                event_volunteer.total_cost = event.price
                event_volunteer.save()
                form = VolunteerEventForm(None)
                events = Event.objects.exclude(evvol__in=vol_events_list)
                form.fields["event"].queryset = (Event.objects.filter(begin_date__year=now.year, begin_date__gte=now,
                                                                      id__in=events) |
                                                 Event.objects.filter(begin_date__year=now.year+1, begin_date__gte=now,
                                                                      id__in=events) |
                                                 Event.objects.filter(end_date__gte=now, id__in=events))\
                    .distinct()\
                    .order_by('begin_date')
                messages.success(request, 'Zapisano na wydarzenie.')
    else:
        form = form_class()
        events = Event.objects.exclude(evvol__in=vol_events_list)
        form.fields["event"].queryset = (Event.objects.filter(begin_date__year=now.year, begin_date__gte=now,
                                                              id__in=events) |
                                         Event.objects.filter(begin_date__year=now.year+1, begin_date__gte=now,
                                                              id__in=events) |
                                         Event.objects.filter(end_date__gte=now, id__in=events))\
            .distinct()\
            .order_by('begin_date')

    return render(request, template_name, {'vol_events_list': vol_events_list, 'form': form,
                                           'prices_json': prices_json})


@login_required
def event_details(request, **kwargs):
    template_name = 'dj/event_details.html'
    event = Event.objects.filter(id=kwargs['pk']).first()
    volunteer = Volunteer.objects.filter(user=request.user)
    event_volunteer = EventVolunteer.objects.filter(event=event, volunteer=volunteer).first()
    return render(request, template_name, {'event': event, 'event_volunteer': event_volunteer})


def music_training_sign(request):
    if request.user.is_authenticated:
        return music_training_view(request)
    else:
        prices_list = RetreatOrMusicTraining.objects.all().values('id', 'base_price', 'sleeping_bag_price',
                                                                  'nights_price', 'additional_night',
                                                                  'with_accommodation', 'with_additional_night')
        prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
        form_class = PersonForm
        form_class2 = MusicTrainingSignForm
        template_name = 'dj/music_training_sign.html'
        today = now
        form = form_class(request.POST or None)
        form2 = form_class2(request.POST or None)
        form2.fields["retreat_or_music_training"].queryset = \
            (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='M') |
             RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='M'))\
            .distinct().order_by('begin_date')
        if request.method == 'POST':
            if form.is_valid() and form2.is_valid():
                music_training = form2.cleaned_data['retreat_or_music_training']
                if music_training is not None:
                    person = form.save(commit=False)
                    person_exists_in_training = \
                        RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=music_training,
                                                                    person__pesel=person.pesel).count()
                    if person_exists_in_training == 0:
                        form.save()
                        training = form2.save()
                        training.person = person
                        volunteer = Volunteer.objects.filter(pesel=person.pesel).first()
                        if volunteer is not None:
                            training.volunteer = volunteer

                        training.save()

                        messages.success(request, 'Zapisano na warsztaty.')

                        return redirect('dj:index')

        else:
            form = form_class()
            form2 = form_class2()
            form2.fields["retreat_or_music_training"].queryset = \
                (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='M') |
                 RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='M'))\
                .distinct().order_by('begin_date')

    return render(request, template_name, {'today': today, 'form': form, 'form2': form2, 'prices_json': prices_json})


def workshop_sign(request):
    if request.user.is_authenticated:
        return workshop_view(request)
    else:
        prices_list = RetreatOrMusicTraining.objects.all().values('id', 'base_price', 'sleeping_bag_price',
                                                                  'nights_price', 'additional_night',
                                                                  'with_accommodation', 'with_additional_night')
        prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
        form_class = PersonForm
        form_class2 = WorkshopSignForm
        template_name = 'dj/workshop_sign.html'
        today = now
        form = form_class(request.POST or None)
        form2 = form_class2(request.POST or None)
        form2.fields["retreat_or_music_training"].queryset = \
            (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='W') |
             RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='W'))\
            .distinct().order_by('begin_date')
        if request.method == 'POST':
            if form.is_valid() and form2.is_valid():
                music_training = form2.cleaned_data['retreat_or_music_training']
                if music_training is not None:
                    person = form.save(commit=False)
                    person_exists_in_training = \
                        RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=music_training,
                                                                    person__pesel=person.pesel).count()
                    if person_exists_in_training == 0:
                        form.save()
                        training = form2.save()
                        training.person = person
                        volunteer = Volunteer.objects.filter(pesel=person.pesel).first()
                        if volunteer is not None:
                            training.volunteer = volunteer

                        training.save()

                        messages.success(request, 'Zapisano na warsztaty.')

                        return redirect('dj:index')

        else:
            form = form_class()
            form2 = form_class2()
            form2.fields["retreat_or_music_training"].queryset = \
                (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='W') |
                 RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='W'))\
                .distinct().order_by('begin_date')

    return render(request, template_name, {'today': today, 'form': form, 'form2': form2, 'prices_json': prices_json})


@login_required
def music_training_view(request):
    prices_list = RetreatOrMusicTraining.objects.all().values('id', 'base_price', 'sleeping_bag_price',
                                                              'nights_price', 'additional_night', 'with_accommodation',
                                                              'with_additional_night')
    prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
    form_class = MusicTrainingVolunteerSignForm
    template_name = 'dj/music_training_view.html'
    today = now
    volunteer = Volunteer.objects.filter(user=request.user).first()
    person = Person.objects.filter(pesel=volunteer.pesel).first()
    if person is None:
        person = Person.objects.create(first_name=volunteer.first_name, surname=volunteer.surname,
                                       pesel=volunteer.pesel, sex=volunteer.sex, age=volunteer.age, city=volunteer.city,
                                       phone_number=volunteer.phone_number, email_address=volunteer.email_address,
                                       address=volunteer.address, zip_code=volunteer.zip_code,
                                       education=volunteer.education)
    training_list = RetreatOrMusicTrainingPerson.objects.filter(volunteer=volunteer,
                                                                retreat_or_music_training__type='M')\
        .order_by('-retreat_or_music_training__begin_date')
    form = form_class(request.POST or None)
    trainings = RetreatOrMusicTraining.objects.exclude(train_person__in=training_list)
    form.fields["retreat_or_music_training"].queryset = \
        (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='M',
                                               id__in=trainings) |
         RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='M',
                                               id__in=trainings))\
        .distinct().order_by('begin_date')
    if request.method == 'POST':
        if form.is_valid():
            music_training = form.cleaned_data['retreat_or_music_training']
            if music_training is not None:
                volunteer_exists_in_training = \
                    RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=music_training,
                                                                volunteer=volunteer).count()
                if volunteer_exists_in_training == 0:
                    training = form.save()
                    training.person = person
                    training.volunteer = volunteer
                    training.how_know_dj = volunteer.how_know_dj
                    training.study = volunteer.study
                    training.work = volunteer.work
                    training.babysitting = volunteer.babysitting
                    training.pensioner = volunteer.pensioner
                    training.unemployed = volunteer.unemployed
                    training.another_work = volunteer.another_work
                    training.guardian_phone_number = volunteer.guardian_phone_number
                    training.sing_or_play = volunteer.sing_or_play
                    training.data_processing_agreement = volunteer.data_processing_agreement
                    training.photographing_agreement = volunteer.photographing_agreement
                    training.save()

                    form = MusicTrainingVolunteerSignForm(None)

                    form.fields["retreat_or_music_training"].queryset = \
                        (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='M',
                                                               id__in=trainings) |
                         RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now,
                                                               type='M', id__in=trainings)) \
                        .distinct().order_by('begin_date')

                    messages.success(request, 'Zapisano na warsztaty.')

    else:
        form = form_class()
        form.fields["retreat_or_music_training"].queryset = \
            (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='M',
                                                   id__in=trainings) |
             RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='W',
                                                   id__in=trainings)) \
            .distinct().order_by('begin_date')

    return render(request, template_name, {'today': today, 'form2': form, 'training_list': training_list,
                                           'prices_json': prices_json})


@login_required
def workshop_view(request):
    prices_list = RetreatOrMusicTraining.objects.all().values('id', 'base_price', 'sleeping_bag_price',
                                                              'nights_price', 'additional_night', 'with_accommodation',
                                                              'with_additional_night')
    prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
    form_class = WorkshopVolunteerSignForm
    template_name = 'dj/workshop_view.html'
    today = now
    volunteer = Volunteer.objects.filter(user=request.user).first()
    person = Person.objects.filter(pesel=volunteer.pesel).first()
    if person is None:
        person = Person.objects.create(first_name=volunteer.first_name, surname=volunteer.surname,
                                       pesel=volunteer.pesel, sex=volunteer.sex, age=volunteer.age, city=volunteer.city,
                                       phone_number=volunteer.phone_number, email_address=volunteer.email_address,
                                       address=volunteer.address, zip_code=volunteer.zip_code,
                                       education=volunteer.education)
    training_list = RetreatOrMusicTrainingPerson.objects.filter(volunteer=volunteer,
                                                                retreat_or_music_training__type='W')\
        .order_by('-retreat_or_music_training__begin_date')
    form = form_class(request.POST or None)
    trainings = RetreatOrMusicTraining.objects.exclude(train_person__in=training_list)
    form.fields["retreat_or_music_training"].queryset = \
        (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='W',
                                               id__in=trainings) |
         RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='W',
                                               id__in=trainings))\
        .distinct().order_by('begin_date')
    if request.method == 'POST':
        if form.is_valid():
            music_training = form.cleaned_data['retreat_or_music_training']
            if music_training is not None:
                volunteer_exists_in_training = \
                    RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=music_training,
                                                                volunteer=volunteer).count()
                if volunteer_exists_in_training == 0:
                    training = form.save()
                    training.person = person
                    training.volunteer = volunteer
                    training.how_know_dj = volunteer.how_know_dj
                    training.study = volunteer.study
                    training.work = volunteer.work
                    training.babysitting = volunteer.babysitting
                    training.pensioner = volunteer.pensioner
                    training.unemployed = volunteer.unemployed
                    training.another_work = volunteer.another_work
                    training.guardian_phone_number = volunteer.guardian_phone_number
                    training.sing_or_play = volunteer.sing_or_play
                    training.data_processing_agreement = volunteer.data_processing_agreement
                    training.photographing_agreement = volunteer.photographing_agreement
                    training.save()

                    form = WorkshopVolunteerSignForm(None)

                    form.fields["retreat_or_music_training"].queryset = \
                        (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='W',
                                                               id__in=trainings) |
                         RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now,
                                                               type='W', id__in=trainings)) \
                        .distinct().order_by('begin_date')

                    messages.success(request, 'Zapisano na warsztaty.')

    else:
        form_class = WorkshopVolunteerSignForm
        form = form_class()
        form.fields["retreat_or_music_training"].queryset = \
            (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='W',
                                                   id__in=trainings) |
             RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='W',
                                                   id__in=trainings)) \
            .distinct().order_by('begin_date')

    return render(request, template_name, {'today': today, 'form2': form, 'training_list': training_list,
                                           'prices_json': prices_json})


@login_required
def music_training_details(request, **kwargs):
    template_name = 'dj/music_training_details.html'
    training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
    volunteer = Volunteer.objects.filter(user=request.user)
    training_volunteer = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=training,
                                                                     volunteer=volunteer).first()
    return render(request, template_name, {'training': training, 'training_volunteer': training_volunteer})


@login_required
def workshop_details(request, **kwargs):
    template_name = 'dj/workshop_details.html'
    training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
    volunteer = Volunteer.objects.filter(user=request.user)
    training_volunteer = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=training,
                                                                     volunteer=volunteer).first()
    return render(request, template_name, {'training': training, 'training_volunteer': training_volunteer})


@login_required
def retreat_details(request, **kwargs):
    template_name = 'dj/retreat_details.html'
    training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
    volunteer = Volunteer.objects.filter(user=request.user)
    training_volunteer = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=training,
                                                                     volunteer=volunteer).first()
    return render(request, template_name, {'training': training, 'training_volunteer': training_volunteer})


def retreat_sign(request):
    if request.user.is_authenticated:
        return retreat_view(request)
    else:
        prices_list = RetreatOrMusicTraining.objects.all().values('id', 'base_price', 'sleeping_bag_price',
                                                                  'nights_price', 'additional_night',
                                                                  'with_accommodation', 'with_additional_night')
        prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
        form_class = ExtendedPersonForm
        form_class2 = RetreatSignForm
        template_name = 'dj/retreat_sign.html'
        today = now
        form = form_class(request.POST or None)
        form2 = form_class2(request.POST or None)
        form2.fields["retreat_or_music_training"].queryset = \
            (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='R') |
             RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='R'))\
            .distinct().order_by('begin_date')
        if request.method == 'POST':
            if form.is_valid() and form2.is_valid():
                music_training = form2.cleaned_data['retreat_or_music_training']
                if music_training is not None:
                    person = form.save(commit=False)
                    person_exists_in_training = \
                        RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=music_training,
                                                                    person__pesel=person.pesel).count()
                    if person_exists_in_training == 0:
                        form.save()
                        training = form2.save()
                        training.person = person
                        volunteer = Volunteer.objects.filter(pesel=person.pesel).first()
                        if volunteer is not None:
                            training.volunteer = volunteer

                        training.save()

                        messages.success(request, 'Zapisano na rekolekcje.')

                        return redirect('dj:index')

        else:
            form = form_class()
            form2 = form_class2()
            form2.fields["retreat_or_music_training"].queryset = \
                (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='R') |
                 RetreatOrMusicTraining.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, type='R'))\
                .distinct().order_by('begin_date')

    return render(request, template_name, {'today': today, 'form': form, 'form2': form2, 'prices_json': prices_json})


@login_required
def retreat_view(request):
    prices_list = RetreatOrMusicTraining.objects.all().values('id', 'base_price', 'sleeping_bag_price',
                                                              'nights_price', 'additional_night', 'with_accommodation',
                                                              'with_additional_night')
    prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
    form_class = RetreatVolunteerSignForm
    template_name = 'dj/retreat_view.html'
    today = now
    volunteer = Volunteer.objects.filter(user=request.user).first()
    person = Person.objects.filter(pesel=volunteer.pesel).first()
    if person is None:
        person = Person.objects.create(first_name=volunteer.first_name, surname=volunteer.surname,
                                       pesel=volunteer.pesel, sex=volunteer.sex, age=volunteer.age, city=volunteer.city,
                                       phone_number=volunteer.phone_number, email_address=volunteer.email_address,
                                       address=volunteer.address, zip_code=volunteer.zip_code,
                                       education=volunteer.education)
    training_list = RetreatOrMusicTrainingPerson.objects.filter(volunteer=volunteer,
                                                                retreat_or_music_training__type='R')\
        .order_by('-retreat_or_music_training__begin_date')
    form = form_class(request.POST or None)
    trainings = RetreatOrMusicTraining.objects.exclude(train_person__in=training_list)
    form.fields["retreat_or_music_training"].queryset = \
        (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='R',
                                               id__in=trainings) |
         RetreatOrMusicTraining.objects.filter(end_date__year=now.year, begin_date__gte=now, type='R',
                                               id__in=trainings))\
        .distinct().order_by('begin_date')
    if request.method == 'POST':
        if form.is_valid():
            music_training = form.cleaned_data['retreat_or_music_training']
            if music_training is not None:
                volunteer_exists_in_training = \
                    RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=music_training,
                                                                volunteer=volunteer).count()
                if volunteer_exists_in_training == 0:
                    training = form.save()
                    training.person = person
                    training.volunteer = volunteer
                    training.how_know_dj = volunteer.how_know_dj
                    training.study = volunteer.study
                    training.work = volunteer.work
                    training.babysitting = volunteer.babysitting
                    training.pensioner = volunteer.pensioner
                    training.unemployed = volunteer.unemployed
                    training.another_work = volunteer.another_work
                    training.guardian_phone_number = volunteer.guardian_phone_number
                    training.sing_or_play = volunteer.sing_or_play
                    training.data_processing_agreement = volunteer.data_processing_agreement
                    training.photographing_agreement = volunteer.photographing_agreement
                    training.save()

                    form = RetreatVolunteerSignForm(None)

                    form.fields["retreat_or_music_training"].queryset = \
                        (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='R',
                                                               id__in=trainings) |
                         RetreatOrMusicTraining.objects.filter(end_date__year=now.year, begin_date__gte=now, type='R',
                                                               id__in=trainings)) \
                        .distinct().order_by('begin_date')

                    messages.success(request, 'Zapisano na rekolekcje.')

    else:
        form = form_class()
        form.fields["retreat_or_music_training"].queryset = \
            (RetreatOrMusicTraining.objects.filter(begin_date__year=now.year, begin_date__gte=now, type='R',
                                                   id__in=trainings) |
             RetreatOrMusicTraining.objects.filter(end_date__year=now.year, begin_date__gte=now, type='R',
                                                   id__in=trainings)) \
            .distinct().order_by('begin_date')

    return render(request, template_name, {'today': today, 'form2': form, 'training_list': training_list,
                                           'prices_json': prices_json})


@login_required
def calendar(request):
    batches_list = Batch.objects.filter(begin_date__month=now.month, begin_date__year=now.year) | \
        Batch.objects.filter(end_date__month=now.month, begin_date__year=now.year)
    events = Event.objects.filter(begin_date__month=now.month, begin_date__year=now.year) | \
        Event.objects.filter(end_date__month=now.month, begin_date__year=now.year)
    trainings = RetreatOrMusicTraining.objects.filter(begin_date__month=now.month, begin_date__year=now.year) | \
        RetreatOrMusicTraining.objects.filter(end_date__month=now.month, begin_date__year=now.year)
    first = now - timedelta(days=now.day - 1)
    month = now.month
    num_list = [6, 13, 20, 27]
    if month in [1, 3, 5, 7, 8, 10, 12]:
        days = 31
    elif month == 2:
        days = 29
    else:
        days = 30

    next = now + timedelta(days=days)

    batches_list_next = Batch.objects.filter(begin_date__month=next.month, begin_date__year=next.year) | \
        Batch.objects.filter(end_date__month=next.month, begin_date__year=next.year)
    events_next = Event.objects.filter(begin_date__month=next.month, begin_date__year=next.year) | \
        Event.objects.filter(end_date__month=next.month, begin_date__year=next.year)
    trainings_next = RetreatOrMusicTraining.objects.filter(begin_date__month=next.month,
                                                           begin_date__year=next.year) | \
        RetreatOrMusicTraining.objects.filter(end_date__month=next.month, begin_date__year=next.year)

    first_next = next - timedelta(days=next.day - 1)
    month_next = next.month

    if month_next in [1, 3, 5, 7, 8, 10, 12]:
        days_next = 31
    elif month == 2:
        days_next = 29
    else:
        days_next = 30

    return render(request, 'dj/calendar.html', {'events': events, 'now': now, 'days': range(days), 'num_list': num_list,
                                                'first': first, 'trainings': trainings, 'batches': batches_list,
                                                'events_next': events_next, 'first_next': first_next,
                                                'next': next, 'batches_list_next': batches_list_next,
                                                'trainings_next': trainings_next, 'days_next': range(days_next)})


@login_required
def photo_edit(request):
    form_class = SetVolunteerPhotoForm
    template_name = 'dj/photo_edit.html'
    volunteer = Volunteer.objects.filter(user=request.user).first()
    form = form_class(request.POST or None, request.FILES, instance=volunteer)
    if request.POST and form.is_valid():
        form.save(commit=False)
        volunteer.save()

        messages.success(request, 'Zdjęcie zostało zaktualizowane.')

        return render(request, 'dj/user_account.html', {'user_details': volunteer})

    return render(request, template_name, {'form': form, 'volunteer': volunteer})


@login_required
def get_files(request):
    template_name = 'dj/files.html'
    files = File.objects.filter(volunteers=True)
    return render(request, template_name, {'files': files})


def remind_password(request):
    form_class = UserRemindPasswordForm
    template_name = 'dj/remind_password.html'

    if request.method == 'POST':
        form = form_class(data=request.POST)
        form.fields['email'].label = "Adres e-mail"

        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email)
            new_password = User.objects.make_random_password()
            for u in user:
                u.set_password(new_password)
                u.save()
                print(new_password)
            if user.count() > 0:
                print(user)

                admin_email = settings.EMAIL_HOST_USER
                to_email = user.first().email

                msg = MIMEMultipart('alternative')
                subject = "Przypomnienie hasła"
                msg['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
                msg['From'] = "Drabina Jakubowa - Centrum Księdza Orione"
                msg['To'] = to_email

                html = render_to_string('dj/includes/password_email.html', {'user': user, 'new_password': new_password})
                part = MIMEText(html, 'html')
                msg.attach(part)

                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                mail.sendmail(admin_email, to_email, msg.as_string())
                mail.quit()

                messages.success(request, 'Wysłano wiadomość na adres e-mail przypisany do konta.')
                return redirect('dj:login')
            else:
                messages.error(request, 'Brak konta powiązanego z tym adresem e-mail.')
    else:
        form = form_class()
        form.fields['email'].label = "Adres e-mail"
    return render(request, template_name, {'form': form})


def event_registration(request):
    if request.user.is_authenticated:
        return events_view(request)
    else:
        prices_list = Event.objects.all().values('id', 'price')
        prices_json = json.dumps(list(prices_list), cls=DjangoJSONEncoder)
        form_class = PersonForm
        form_class2 = EventSignForm
        template_name = 'dj/event_simple_registration.html'
        today = now
        form = form_class(request.POST or None)
        form2 = form_class2(request.POST or None)
        form2.fields["event"].queryset = \
            (Event.objects.filter(begin_date__year=now.year, begin_date__gte=now, account_needed=False) |
             Event.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, account_needed=False))\
            .distinct().order_by('begin_date')
        if request.method == 'POST':
            if form.is_valid() and form2.is_valid():
                event = form2.cleaned_data['event']
                if event is not None:
                    person = form.save(commit=False)
                    person_exists_in_event = \
                        EventPerson.objects.filter(event=event, person__email_address=person.email_address).count()
                    if person_exists_in_event == 0:
                        form.save()
                        event_person = form2.save()
                        event_person.person = person
                        volunteer = Volunteer.objects.filter(email_address=person.email_address).first()
                        if volunteer is not None:
                            event_person.volunteer = volunteer

                        event_person.save()

                        messages.success(request, 'Zapisano na wydarzenie.')

                        return redirect('dj:index')

        else:
            form = form_class()
            form2 = form_class2()
            form2.fields["event"].queryset = \
                (Event.objects.filter(begin_date__year=now.year, begin_date__gte=now, account_needed=False) |
                 Event.objects.filter(begin_date__year=now.year+1, begin_date__gte=now, account_needed=False))\
                .distinct().order_by('begin_date')

    return render(request, template_name, {'today': today, 'user_form': form, 'event_person': form2,
                                           'prices_json': prices_json})
