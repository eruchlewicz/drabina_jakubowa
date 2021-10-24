from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from easy_pdf.views import PDFTemplateResponseMixin
from django.views.generic import DetailView, ListView
from django.utils import timezone
from datetime import timedelta
from graphos.renderers.gchart import PieChart
from graphos.sources.model import ModelDataSource
from coordinatepanel.templatetags.auth_extras import *
from django.contrib import messages

now = timezone.now()


def coordinator_login(request):
    form_class = AuthenticationForm
    template_name = 'coordinatepanel/coordinator_login.html'

    if request.method == 'POST':
        form = form_class(data=request.POST)
        form.fields['password'].label = "Hasło"
        form.fields['username'].label = "Nazwa użytkownika"
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                if user.groups.filter(name='Koordynatorzy').exists():
                    login(request, user)
                    return redirect('coordinatepanel:batches')
    else:
        form = form_class()
        form.fields['password'].label = "Hasło"
        form.fields['username'].label = "Nazwa użytkownika"
    return render(request, template_name, {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('coordinatepanel:coordinator_login')


@login_required
def batches(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        coordinator = Coordinator.objects.filter(user=user).first()
        volunteer = coordinator.volunteer
        batch_volunteer_list = BatchVolunteer.objects.filter(volunteer=volunteer)
        batches_list = Batch.objects.filter(main_coordinator=coordinator).order_by('-begin_date') | \
            Batch.objects.filter(auxiliary_coordinator=coordinator).order_by('-begin_date')
        return render(request, 'coordinatepanel/batches.html', {'batches_list': batches_list, 'now': now,
                                                                'batch_volunteer_list': batch_volunteer_list,
                                                                'coordinator': coordinator})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def volunteers(request, **kwargs):
    template_name = 'coordinatepanel/volunteers.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        batch_volunteers_male = BatchVolunteer.objects.filter(batch__id=kwargs['pk'], volunteer__sex='M',
                                                              reserve_list=False)\
            .order_by('sign_date', 'volunteer__surname')
        batch_volunteers_female = BatchVolunteer.objects.filter(batch__id=kwargs['pk'], volunteer__sex='K',
                                                                reserve_list=False)\
            .order_by('sign_date', 'volunteer__surname')
        batch_volunteers_reserve_male = BatchVolunteer.objects.filter(batch__id=kwargs['pk'], reserve_list=True,
                                                                      volunteer__sex='M')\
            .order_by('sign_date', 'volunteer__surname')
        batch_volunteers_reserve_female = BatchVolunteer.objects.filter(batch__id=kwargs['pk'], reserve_list=True,
                                                                        volunteer__sex='K')\
            .order_by('sign_date', 'volunteer__surname')
        batch_id = kwargs['pk']
        batch = Batch.objects.filter(id=batch_id).first()

        return render(request, template_name, {'batch_volunteers_male': batch_volunteers_male, 'batch_id': batch_id,
                                               'batch_volunteers_female': batch_volunteers_female, 'batch': batch,
                                               'now': now,
                                               'batch_volunteers_reserve_male': batch_volunteers_reserve_male,
                                               'batch_volunteers_reserve_female': batch_volunteers_reserve_female})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def participants(request, **kwargs):
    template_name = 'coordinatepanel/participants.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        batch_participants_male = BatchParticipant.objects.filter(batch__id=kwargs['pk'], reserve_list=False,
                                                                  participant__sex='M')\
            .order_by('sign_date', 'participant__surname')
        batch_participants_female = BatchParticipant.objects.filter(batch__id=kwargs['pk'], reserve_list=False,
                                                                    participant__sex='K')\
            .order_by('sign_date', 'participant__surname')
        batch_participants_reserve_male = BatchParticipant.objects.filter(batch__id=kwargs['pk'], reserve_list=True,
                                                                          participant__sex='M')\
            .order_by('sign_date', 'participant__surname')
        batch_participants_reserve_female = BatchParticipant.objects.filter(batch__id=kwargs['pk'], reserve_list=True,
                                                                            participant__sex='K')\
            .order_by('sign_date', 'participant__surname')
        batch_id = kwargs['pk']
        batch = Batch.objects.filter(id=batch_id).first()
        return render(request, template_name, {'batch_participants_male': batch_participants_male, 'batch_id': batch_id,
                                               'batch_participants_female': batch_participants_female, 'now': now,
                                               'batch_participants_reserve_male': batch_participants_reserve_male,
                                               'batch_participants_reserve_female': batch_participants_reserve_female,
                                               'batch': batch})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def batch_view(request, **kwargs):
    template_name = 'coordinatepanel/batch_details.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        batch_details = Batch.objects.filter(id=kwargs['pk']).first()
        summary = BatchParticipant.objects.filter(batch=batch_details).count()
        men = BatchParticipant.objects.filter(batch=batch_details, participant__sex='M').count()
        men_wheelchair = BatchParticipant.objects.filter(batch=batch_details, participant__sex='M',
                                                         participant__bear=True).count()
        women = BatchParticipant.objects.filter(batch=batch_details, participant__sex='K').count()
        women_wheelchair = BatchParticipant.objects.filter(batch=batch_details, participant__sex='K',
                                                           participant__bear=True).count()
        batch_participants = BatchParticipant.objects.filter(batch=batch_details)
        batch_volunteers = BatchVolunteer.objects.filter(batch=batch_details)
        participant_points = sum(
            [
                sum([bp.participant.k_1, bp.participant.k_2, bp.participant.k_3])
                for bp in batch_participants
            ]
        )
        volunteer_points = sum(
            [
                sum([bv.volunteer.experience, bv.volunteer.physical_performance])
                for bv in batch_volunteers
            ]
        )

        return render(
            request,
            template_name,
            {
                'batch_details': batch_details,
                'summary': summary,
                'men': men,
                'men_wheelchair': men_wheelchair,
                'women': women,
                'women_wheelchair': women_wheelchair,
                'participant_points': participant_points,
                'volunteer_points': volunteer_points
            }
        )
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def batch_volunteer_edit(request, **kwargs):
    form_class = BatchVolunteerForm
    template_name = 'coordinatepanel/batch_volunteer_edit.html'
    batch_volunteer = BatchVolunteer.objects.filter(batch=kwargs['pk'], volunteer=kwargs['batch_volunteer_id']).first()
    batch = Batch.objects.filter(id=kwargs['pk']).first()
    volunteer = Volunteer.objects.filter(id=kwargs['batch_volunteer_id']).first()
    rooms = Room.objects.all()
    form = form_class(request.POST or None, instance=batch_volunteer)
    form.fields["room"].queryset = empty_rooms_volunteer(batch, batch_volunteer)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            batch_volunteer.room_sex = volunteer.sex
            batch_volunteer.save()
            if abs(batch.begin_date - batch_volunteer.batch_begin_date).days == 1:
                batch_volunteer.training_days = 1
                batch_volunteer.batch_days = abs(
                    batch_volunteer.batch_end_date - batch_volunteer.batch_begin_date).days
            elif abs(batch.begin_date - batch_volunteer.batch_begin_date).days == 2:
                batch_volunteer.training_days = 0
                batch_volunteer.batch_days = abs(
                    batch_volunteer.batch_end_date - batch_volunteer.batch_begin_date).days + 1
            else:
                batch_volunteer.batch_days = abs(
                    batch_volunteer.batch_end_date - batch_volunteer.batch_begin_date).days - 1

            batch_volunteer.save()

            messages.success(request, 'Zapisano zmiany.')

            return redirect('coordinatepanel:volunteers_list', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'rooms': rooms,
                                           'batch_volunteer': batch_volunteer})


@login_required
def batch_participant_edit(request, **kwargs):
    form_class = BatchParticipantForm
    template_name = 'coordinatepanel/batch_participant_edit.html'
    batch_participant = BatchParticipant.objects.filter(batch=kwargs['pk'],
                                                        participant=kwargs['batch_participant_id']).first()
    participant = Participant.objects.filter(id=kwargs['batch_participant_id']).first()
    rooms = Room.objects.all()
    batch = Batch.objects.filter(id=kwargs['pk']).first()
    # nurses = batch.nurse.all()
    # doctors = batch.doctor.all()
    # vol_nurses = Volunteer.objects.filter(nurvol__in=nurses)
    # vol_doctors = Volunteer.objects.filter(docvol__in=doctors)
    coordinator = batch.main_coordinator.volunteer
    auxiliary_coordinator = batch.auxiliary_coordinator
    if auxiliary_coordinator is not None:
        auxiliary_coordinator = batch.auxiliary_coordinator.volunteer
        volunteers_list = BatchVolunteer.objects.filter(batch=kwargs['pk'])
    else:
        volunteers_list = BatchVolunteer.objects.filter(batch=kwargs['pk'])
    form = form_class(request.POST or None, instance=batch_participant)
    form.fields["volunteer"].queryset = Volunteer.objects.filter(vol__in=volunteers_list)
    form.fields["room"].queryset = empty_rooms_participant(batch, batch_participant)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            batch_participant.room_sex = participant.sex
            batch_participant.save()

            messages.success(request, 'Zapisano zmiany.')

            return redirect('coordinatepanel:participants_list', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'rooms': rooms,
                                           'batch_participant': batch_participant})


@login_required
def delete_participant(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        query = BatchParticipant.objects.filter(id=kwargs['batch_participant_id']).first()
        batch_id = query.batch.id
        batch = Batch.objects.filter(id=batch_id).first()
        batch.participants -= 1
        batch.save()
        query.delete()

        messages.info(request, 'Podopieczny został wypisany z turnusu.')

        return HttpResponseRedirect(reverse('coordinatepanel:participants_list', kwargs={'pk': batch_id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def delete_volunteer(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        query = BatchVolunteer.objects.get(id=kwargs['batch_volunteer_id'])
        batch_id = query.batch.id
        batch = Batch.objects.filter(id=batch_id).first()
        batch.volunteers -= 1
        batch.save()
        query.delete()

        messages.info(request, 'Wolontariusz został wypisany z turnusu.')

        return HttpResponseRedirect(reverse('coordinatepanel:volunteers_list', kwargs={'pk': batch_id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def participant_details(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        participant = Participant.objects.filter(id=kwargs['participant_id']).first()
        batch = Batch.objects.filter(id=kwargs["pk"]).first()
        all_batches = BatchParticipant.objects.filter(participant=participant)
        return render(request, 'coordinatepanel/participant_details.html', {'batch_id': batch.id, 'batch': batch,
                                                                            'participant': participant,
                                                                            'all_batches': all_batches})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def volunteer_details(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        volunteer = Volunteer.objects.filter(id=kwargs['volunteer_id']).first()
        batch = Batch.objects.filter(id=kwargs["pk"]).first()
        all_batches = BatchVolunteer.objects.filter(volunteer=volunteer)
        return render(request, 'coordinatepanel/volunteer_details.html', {'batch_id': kwargs["pk"], 'batch': batch,
                                                                          'volunteer': volunteer,
                                                                          'all_batches': all_batches})
    else:
        return redirect('coordinatepanel:coordinator_login')


class ParticipantCertificatePDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'coordinatepanel/certificate/participant-certificate.html'
    download_filename = 'certificate.pdf'
    model = BatchParticipant

    def get_object(self, queryset=None):
        obj = BatchParticipant.objects.filter(unique_key=self.kwargs["id"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(ParticipantCertificatePDFView, self).get_context_data(
            pagesize='A4',
            title='Zaświadczenie',
            congregation=Congregation.objects.first(),
            home=Home.objects.first(),
            date=now,
            **kwargs
        )


class CertificatePDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'coordinatepanel/certificate/certificate.html'
    download_filename = 'certificate.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(unique_key=self.kwargs["id"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(CertificatePDFView, self).get_context_data(
            pagesize='A4',
            title='Zaświadczenie',
            congregation=Congregation.objects.first(),
            home=Home.objects.first(),
            date=now,
            **kwargs
        )


class VolunteerContractPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'coordinatepanel/contract/contract.html'
    download_filename = 'contract.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(unique_key=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(VolunteerContractPDFView, self).get_context_data(
            pagesize='A4',
            title='Umowa',
            congregation=Congregation.objects.first(),
            date=now,
            **kwargs
        )


class AllVolunteersContractPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/contract/all_contracts.html'
    download_filename = 'contracts.pdf'
    model = BatchVolunteer

    def get_context_data(self, **kwargs):
        return super(AllVolunteersContractPDFView, self).get_context_data(
            pagesize='A4',
            title='Umowy',
            congregation=Congregation.objects.first(),
            all_volunteers=BatchVolunteer.objects.filter(batch__id=self.kwargs["pk"]),
            date=now,
            **kwargs
        )


class ContractPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'coordinatepanel/contract/coordinator_contract.html'
    download_filename = 'contract.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(unique_key=self.kwargs["pk"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(ContractPDFView, self).get_context_data(
            pagesize='A4',
            title='Umowa',
            congregation=Congregation.objects.first(),
            date=now,
            **kwargs
        )


class VolunteersReportPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/reports/volunteers_report.html'
    download_filename = 'volunteers-report.pdf'
    model = BatchVolunteer

    def get_context_data(self, **kwargs):
        return super(VolunteersReportPDFView, self).get_context_data(
            pagesize='A4',
            title='Raport',
            date=now,
            batchvolunteers=BatchVolunteer.objects.filter(batch=self.kwargs["pk"]).order_by('volunteer__sex',
                                                                                            'volunteer__surname'),
            batchparticipants=BatchParticipant.objects.filter(batch=self.kwargs["pk"]),
            **kwargs
        )


class ParticipantsReportPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/reports/participants_report.html'
    download_filename = 'participants-report.pdf'
    model = BatchParticipant

    def get_context_data(self, **kwargs):
        return super(ParticipantsReportPDFView, self).get_context_data(
            pagesize='A4',
            title='Raport',
            date=now,
            batchparticipants=BatchParticipant.objects.filter(batch=self.kwargs["pk"], reserve_list=False)
            .order_by('participant__sex', 'participant__surname'),
            reserveparticipants=BatchParticipant.objects.filter(batch=self.kwargs["pk"], reserve_list=True)
            .order_by('participant__sex', 'participant__surname'),
            batchvolunteers=BatchVolunteer.objects.filter(batch=self.kwargs["pk"]),
            **kwargs
        )


class RoomsReportPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/reports/rooms_report.html'
    download_filename = 'rooms-report.pdf'
    model = Room

    def get_context_data(self, **kwargs):
        return super(RoomsReportPDFView, self).get_context_data(
            pagesize='A4',
            title='Raport',
            date=now,
            batchparticipants=BatchParticipant.objects.filter(batch=self.kwargs["pk"]),
            batchvolunteers=BatchVolunteer.objects.filter(batch=self.kwargs["pk"]),
            **kwargs
        )


class RoomsEmptyReportPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/reports/rooms_empty_report.html'
    download_filename = 'empty-rooms-report.pdf'
    model = Room

    def get_context_data(self, **kwargs):
        return super(RoomsEmptyReportPDFView, self).get_context_data(
            pagesize='A4',
            title='Pusty raport',
            **kwargs,
        )


class CirculationCardPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'coordinatepanel/reports/circulation_card.html'
    download_filename = 'circulation_card.pdf'
    model = BatchVolunteer

    def get_context_data(self, **kwargs):
        return super(CirculationCardPDFView, self).get_context_data(
            coordinator=Coordinator.objects.filter(user=self.request.user).first(),
            batch=Batch.objects.filter(id=self.kwargs["pk"]).first(),
            pagesize='A4 landscape',
            title='Karta obiegowa',
            **kwargs,
        )


def statistics(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        batches_year = Batch.objects.filter(begin_date__year=now.year) | Batch.objects.filter(end_date__year=now.year)
        for batch in batches_year:
            all_participants_on_batch = BatchParticipant.objects.filter(batch=batch).count()
            all_volunteers_on_batch = BatchVolunteer.objects.filter(batch=batch).count()
            batch.participants = all_participants_on_batch
            batch.volunteers = all_volunteers_on_batch
            batch.save()

        queryset = Batch.objects.filter(begin_date__year=now.year) | \
            Batch.objects.filter(end_date__year=now.year)

        data_source = ModelDataSource(queryset, fields=['__str__', 'volunteers'])
        data_source2 = ModelDataSource(queryset, fields=['__str__', 'participants'])

        chart = PieChart(data_source, options={'title': 'Wolontariusze', 'pieSliceText': 'value'})
        chart2 = PieChart(data_source2, options={'title': 'Podopieczni', 'pieSliceText': 'value'})

        return render(request, 'coordinatepanel/charts/overall_chart.html', {'chart': chart, 'chart2': chart2,
                                                                             'now': now})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def events_view(request):
    template_name = 'coordinatepanel/events.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        coordinator = Coordinator.objects.filter(user=user).first()
        volunteer = coordinator.volunteer
        vol_events_list = EventVolunteer.objects.filter(volunteer=volunteer).order_by('-event__begin_date')
        events_list = Event.objects.filter(main_coordinator=coordinator).order_by('-begin_date') | \
            Event.objects.filter(auxiliary_coordinator=coordinator).order_by('-begin_date')
        return render(request, template_name, {'events_list': events_list, 'now': now,
                                               'vol_events_list': vol_events_list, 'coordinator': coordinator})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def event_details(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        template_name = 'coordinatepanel/event_details.html'
        event = Event.objects.filter(id=kwargs['pk']).first()
        volunteer = Volunteer.objects.filter(user=request.user)
        event_volunteer = EventVolunteer.objects.filter(event=event, volunteer=volunteer).first()
        return render(request, template_name, {'event': event, 'event_volunteer': event_volunteer})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def event_volunteers(request, **kwargs):
    template_name = 'coordinatepanel/event_volunteers.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        event_volunteers_list = EventVolunteer.objects.filter(event__id=kwargs['pk']).order_by("volunteer__surname")
        event_id = kwargs['pk']
        event = Event.objects.filter(id=event_id).first()
        return render(request, template_name, {'event_volunteers_list': event_volunteers_list, 'event_id': event_id,
                                               'event': event, 'now': now})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def event_participants(request, **kwargs):
    template_name = 'coordinatepanel/event_participants.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        event_participants_list = EventParticipant.objects.filter(event__id=kwargs['pk'])\
            .order_by("participant__surname")
        event_id = kwargs['pk']
        event = Event.objects.filter(id=event_id).first()
        return render(request, template_name, {'event_participants_list': event_participants_list, 'event_id': event_id,
                                               'event': event, 'now': now})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def event_volunteer_details(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        volunteer = Volunteer.objects.filter(id=kwargs['volunteer_id']).first()
        event = Event.objects.filter(id=kwargs["pk"]).first()
        return render(request, 'coordinatepanel/volunteer_details.html', {'event_id': kwargs["pk"], 'event': event,
                                                                          'volunteer': volunteer})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def event_participant_details(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        participant = Participant.objects.filter(id=kwargs['participant_id']).first()
        event = Event.objects.filter(id=kwargs["pk"]).first()
        return render(request, 'coordinatepanel/participant_details.html', {'event_id': kwargs["pk"], 'event': event,
                                                                            'participant': participant})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def event_participant_edit(request, **kwargs):
    user = request.user
    form_class = EventParticipantForm
    template_name = 'coordinatepanel/event_participant_edit.html'
    event = Event.objects.filter(id=kwargs["pk"]).first()
    event_participant = EventParticipant.objects.filter(id=kwargs["event_participant_id"]).first()

    volunteers_list = EventVolunteer.objects.filter(event=event)
    form = form_class(request.POST or None, instance=event_participant)
    form.fields["volunteer"].queryset = Volunteer.objects.filter(volo__in=volunteers_list)
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            event_participant.save()

            messages.success(request, 'Zapisano zmiany.')

            return redirect('coordinatepanel:event_participants', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'event_participant': event_participant})


@login_required
def delete_event_participant(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        query = EventParticipant.objects.filter(id=kwargs['event_participant_id']).first()
        event_id = query.event.id
        event = Event.objects.filter(id=event_id).first()
        event.participants -= 1
        event.save()
        query.delete()

        messages.info(request, 'Podopieczny został wypisany z wydarzenia.')

        return HttpResponseRedirect(reverse('coordinatepanel:event_participants', kwargs={'pk': event_id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def delete_event_volunteer(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        query = EventVolunteer.objects.get(id=kwargs['event_volunteer_id'])
        event_id = query.event.id
        event = Batch.objects.filter(id=event_id).first()
        event.volunteers -= 1
        event.save()
        query.delete()

        messages.info(request, 'Wolontariusz został wypisany z wydarzenia.')

        return HttpResponseRedirect(reverse('coordinatepanel:event_volunteers', kwargs={'pk': event_id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


class EventReportPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/reports/event_report.html'
    download_filename = 'event-report.pdf'
    model = EventParticipant

    def get_context_data(self, **kwargs):
        return super(EventReportPDFView, self).get_context_data(
            pagesize='A4',
            title='Raport wydarzenia',
            date=now,
            eventparticipants=EventParticipant.objects.filter(event=self.kwargs["pk"]).order_by('participant__sex',
                                                                                                'participant__surname'),
            eventvolunteers=EventVolunteer.objects.filter(event=self.kwargs["pk"]).order_by('volunteer__sex',
                                                                                            'volunteer__surname'),
            event=Event.objects.filter(id=self.kwargs["pk"]).first(),
            **kwargs
        )


class EventReportListPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/reports/event_report_list.html'
    download_filename = 'event-list.pdf'
    model = EventParticipant

    def get_context_data(self, **kwargs):
        return super(EventReportListPDFView, self).get_context_data(
            pagesize='A4',
            title='Lista wydarzenia',
            date=now,
            eventparticipants=EventParticipant.objects.filter(event=self.kwargs["pk"]).order_by('participant__surname'),
            eventvolunteers=EventVolunteer.objects.filter(event=self.kwargs["pk"]).order_by('volunteer__surname'),
            event=Event.objects.filter(id=self.kwargs["pk"]).first(),
            **kwargs
        )


@login_required
def music_trainings(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        coordinator = Coordinator.objects.filter(user=user).first()
        training_list = RetreatOrMusicTraining.objects.filter(main_coordinator=coordinator)\
            .order_by('-begin_date') | \
            RetreatOrMusicTraining.objects.filter(auxiliary_coordinator=coordinator).order_by('-begin_date')
        return render(request, 'coordinatepanel/trainings.html', {'training_list': training_list, 'now': now,
                                                                  'coordinator': coordinator})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def training_details(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        template_name = 'coordinatepanel/training_details.html'
        training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
        volunteer = Volunteer.objects.filter(user=request.user)
        training_volunteer = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=training,
                                                                         volunteer=volunteer).first()
        return render(request, template_name, {'training': training, 'event_volunteer': training_volunteer})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def training_people(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        template_name = 'coordinatepanel/training_people.html'
        training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
        training_people_list = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=training)
        return render(request, template_name, {'training': training, 'training_people_list': training_people_list,
                                               'now': now})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def person_details(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
        training_person = RetreatOrMusicTrainingPerson.objects.filter(person__id=kwargs['person_id'],
                                                                      retreat_or_music_training=training).first()
        return render(request, 'coordinatepanel/person.html', {'training': training,
                                                               'training_person': training_person})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def delete_person(request, **kwargs):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        query = RetreatOrMusicTrainingPerson.objects.get(id=kwargs['training_person_id'])
        training_id = query.retreat_or_music_training.id
        training = RetreatOrMusicTraining.objects.filter(id=training_id).first()
        training.people -= 1
        training.save()
        query.delete()

        messages.info(request, 'Uczestnik został wypisany.')

        return HttpResponseRedirect(reverse('coordinatepanel:training_people', kwargs={'pk': training_id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def training_person_edit(request, **kwargs):
    form_class = RetreatOrMusicTrainingPersonForm
    template_name = 'coordinatepanel/training_person_edit.html'
    training_person = RetreatOrMusicTrainingPerson.objects.filter(id=kwargs['training_person_id']).first()
    person = training_person.person
    training = training_person.retreat_or_music_training
    form = form_class(request.POST or None, instance=training_person)
    form.fields["room"].queryset = empty_rooms_person(training, training_person)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            training_person.room_sex = person.sex
            training_person.save()

            messages.success(request, 'Zapisano zmiany.')

            return redirect('coordinatepanel:training_people', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'training_person': training_person})


class TrainingReportPDFView(PDFTemplateResponseMixin, ListView):
    template_name = 'coordinatepanel/reports/training_report.html'
    download_filename = 'training-report.pdf'
    model = RetreatOrMusicTrainingPerson

    def get_context_data(self, **kwargs):
        return super(TrainingReportPDFView, self).get_context_data(
            pagesize='A4',
            title='Raport',
            date=now,
            trainingperson=RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=self.kwargs["pk"])
            .order_by('voice', 'person__surname'),
            training=RetreatOrMusicTraining.objects.filter(id=self.kwargs["pk"]).first(),
            **kwargs
        )


@login_required
def event_volunteer_payment(request, **kwargs):
    form_class = EventVolunteerPaymentForm
    template_name = 'coordinatepanel/event_volunteer_payment.html'
    event_volunteer = EventVolunteer.objects.filter(id=kwargs['event_volunteer_id']).first()
    form = form_class(request.POST or None, instance=event_volunteer)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            event_volunteer.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('coordinatepanel:event_volunteers', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'event_volunteer': event_volunteer})


@login_required
def event_participant_payment(request, **kwargs):
    form_class = EventParticipantPaymentForm
    template_name = 'coordinatepanel/event_participant_payment.html'
    event_participant = EventParticipant.objects.filter(id=kwargs['event_participant_id']).first()
    form = form_class(request.POST or None, instance=event_participant)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            event_participant.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('coordinatepanel:event_participants', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'event_participant': event_participant})


@login_required
def person_payment(request, **kwargs):
    form_class = PersonPaymentForm
    template_name = 'coordinatepanel/person_payment.html'
    training_person = RetreatOrMusicTrainingPerson.objects.filter(id=kwargs['training_person_id']).first()
    form = form_class(request.POST or None, instance=training_person)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            training_person.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('coordinatepanel:training_people', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'training_person': training_person})


@login_required
def participant_payment(request, **kwargs):
    form_class = PaymentForm
    template_name = 'coordinatepanel/batch_participant_payment.html'
    batch_participant = BatchParticipant.objects.filter(id=kwargs['batch_participant_id']).first()
    form = form_class(request.POST or None, instance=batch_participant)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            batch_participant.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('coordinatepanel:participants_list', batch_participant.batch.id)
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'batch_participant': batch_participant})


@login_required
def calendar(request):
    user = request.user
    coordinator = Coordinator.objects.filter(user=user).first()
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        bookings = Booking.objects.filter(begin_date__month=now.month, begin_date__year=now.year,
                                          room__isnull=False) | \
            Booking.objects.filter(end_date__month=now.month, begin_date__year=now.year, room__isnull=False)
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

        bookings_next = Booking.objects.filter(begin_date__month=next.month, begin_date__year=next.year,
                                               room__isnull=False) | \
            Booking.objects.filter(end_date__month=next.month, begin_date__year=next.year, room__isnull=False)
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

        return render(request, 'coordinatepanel/calendar.html', {'events': events, 'now': now, 'days': range(days),
                                                                 'num_list': num_list, 'first': first,
                                                                 'trainings': trainings, 'batches': batches_list,
                                                                 'next': next, 'batches_list_next': batches_list_next,
                                                                 'events_next': events_next, 'first_next': first_next,
                                                                 'trainings_next': trainings_next,
                                                                 'days_next': range(days_next), 'bookings': bookings,
                                                                 'bookings_next': bookings_next,
                                                                 'coordinator': coordinator})
    else:
        return redirect('coordinatepanel:home_coordinator_login')


@login_required
def participant_photo_edit(request, **kwargs):
    form_class = SetParticipantPhotoForm
    template_name = 'coordinatepanel/participant_photo_edit.html'
    participant = Participant.objects.filter(id=kwargs['participant_id']).first()
    batch = Batch.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, request.FILES, instance=participant)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            participant.save()

            messages.success(request, 'Zdjęcie zostało zaktualizowane.')

            return render(request, 'coordinatepanel/participant_details.html', {'batch_id': batch.id, 'batch': batch,
                                                                                'participant': participant})
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'participant': participant})


@login_required
def move_participant_to_base_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        participant = Participant.objects.filter(id=kwargs['participant_id'])
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        batch_participant = BatchParticipant.objects.get(participant=participant, batch=batch)
        batch_participant.reserve_list = False
        batch_participant.save()

        messages.success(request, 'Podopieczny został wpisany na listę podstawową.')

        return HttpResponseRedirect(reverse('coordinatepanel:participants_list', kwargs={'pk': batch.id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def move_participant_to_reserve_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        participant = Participant.objects.filter(id=kwargs['participant_id'])
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        batch_participant = BatchParticipant.objects.get(participant=participant, batch=batch)
        batch_participant.reserve_list = True
        batch_participant.save()

        messages.success(request, 'Podopieczny został wpisany na listę rezerwową.')

        return HttpResponseRedirect(reverse('coordinatepanel:participants_list', kwargs={'pk': batch.id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def move_volunteer_to_base_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        volunteer = Volunteer.objects.filter(id=kwargs['volunteer_id'])
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        batch_volunteer = BatchVolunteer.objects.get(volunteer=volunteer, batch=batch)
        batch_volunteer.reserve_list = False
        batch_volunteer.save()

        messages.success(request, 'Wolontariusz został wpisany na listę podstawową.')

        return HttpResponseRedirect(reverse('coordinatepanel:volunteers_list', kwargs={'pk': batch.id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def move_volunteer_to_reserve_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        volunteer = Volunteer.objects.filter(id=kwargs['volunteer_id'])
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        batch_volunteer = BatchVolunteer.objects.get(volunteer=volunteer, batch=batch)
        batch_volunteer.reserve_list = True
        batch_volunteer.save()

        messages.success(request, 'Wolontariusz został wpisany na listę rezerwową.')

        return HttpResponseRedirect(reverse('coordinatepanel:volunteers_list', kwargs={'pk': batch.id}))
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def get_files(request):
    template_name = 'coordinatepanel/files.html'
    form_class = UploadFileForm
    form = form_class(request.POST or None, request.FILES)
    files = File.objects.filter(coordinators=True)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.method == 'POST' and form.is_valid():
            file = form.save(commit=False)
            file.coordinators = True
            file.save()

            messages.success(request, 'Plik został dodany.')

            return render(request, template_name, {'form': form, 'files': files})
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'files': files})


@login_required
def update_participants_count(request):
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        batches_year = Batch.objects.filter(begin_date__year=now.year) | Batch.objects.filter(end_date__year=now.year)
        for batch in batches_year:
            all_participants_on_batch = BatchParticipant.objects.filter(batch=batch).count()
            all_volunteers_on_batch = BatchVolunteer.objects.filter(batch=batch).count()
            batch.participants = all_participants_on_batch
            batch.volunteers = all_volunteers_on_batch
            batch.save()
        return redirect('coordinatepanel:statistics')
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def event_info_edit(request, **kwargs):
    form_class = EventInformationForm
    template_name = 'coordinatepanel/event_info_edit.html'
    event = Event.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=event)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            event.save()

            messages.success(request, 'Informacja została zapisana.')

            return redirect('coordinatepanel:event_details', kwargs['pk'])
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'event': event})


class NurseContractPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'dj/contract/nurse_contract.html'
    download_filename = 'contract.pdf'
    model = BatchVolunteer

    def get_object(self, queryset=None):
        obj = BatchVolunteer.objects.filter(id=self.kwargs["pk"]).first()
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
        obj = BatchVolunteer.objects.filter(id=self.kwargs["pk"]).first()
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


@login_required
def email_addresses(request, **kwargs):
    template_name = 'coordinatepanel/email_addresses.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy']).exists():
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        batch_volunteers = BatchVolunteer.objects.filter(batch__id=batch.id)
        return render(request, template_name, {'batch_volunteers': batch_volunteers})
    else:
        return redirect('coordinatepanel:coordinator_login')


@login_required
def edit_participant(request, **kwargs):
    form_class = ParticipantForm
    template_name = 'coordinatepanel/edit_participant.html'
    participant = Participant.objects.filter(id=kwargs['participant_id']).first()
    batch = Batch.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=participant)
    if request.user.groups.filter(name__in=['Koordynatorzy']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            participant.save()

            messages.success(request, 'Dane zostały zapiane.')

            return render(request, 'coordinatepanel/participant_details.html', {'batch_id': batch.id, 'batch': batch,
                                                                                'participant': participant})
    else:
        return redirect('coordinatepanel:coordinator_login')

    return render(request, template_name, {'form': form, 'participant': participant})
