from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
import smtplib
from django.conf import settings
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from easy_pdf.views import PDFTemplateResponseMixin
from django.views.generic import DetailView
from coordinatepanel.templatetags.auth_extras import *
from django.contrib import messages
import csv
import pandas

now = timezone.now()


def home_coordinator_login(request):
    form_class = AuthenticationForm
    template_name = 'homepanel/home_coordinator_login.html'

    if request.method == 'POST':
        form = form_class(data=request.POST)
        form.fields['password'].label = "Hasło"
        form.fields['username'].label = "Nazwa użytkownika"
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                if user.groups.filter(name='Koordynatorzy domu').exists():
                    login(request, user)
                    return redirect('homepanel:all_bookings')
                elif user.groups.filter(name='Koordynatorzy zapisów').exists():
                    login(request, user)
                    return redirect('homepanel:all_participants')
    else:
        form = form_class()
        form.fields['password'].label = "Hasło"
        form.fields['username'].label = "Nazwa użytkownika"
    return render(request, template_name, {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('homepanel:home_coordinator_login')


@login_required
def batches(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        batches_all = Batch.objects.all().order_by('-begin_date')
        paginator = Paginator(batches_all, 15)
        page = request.GET.get('page', 1)
        try:
            batches_list = paginator.page(page)
        except PageNotAnInteger:
            batches_list = paginator.page(1)
        except EmptyPage:
            batches_list = paginator.page(paginator.num_pages)
        return render(request, 'homepanel/batches.html', {'batches_list': batches_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def volunteers(request, **kwargs):
    template_name = 'homepanel/volunteers.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        batch_volunteers = BatchVolunteer.objects.filter(batch__id=kwargs['pk']).order_by('volunteer__surname')
        batch_id = kwargs['pk']
        return render(request, template_name, {'batch_volunteers': batch_volunteers, 'batch_id': batch_id})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def participants(request, **kwargs):
    template_name = 'homepanel/participants.html'
    user = request.user
    future_batches = (Batch.objects.filter(begin_date__year=now.year, end_date__gte=now) |
                      Batch.objects.filter(begin_date__year=now.year + 1, end_date__gte=now)).order_by('begin_date')
    item_list = "["
    first = True

    for b in future_batches:
        men = BatchParticipant.objects.filter(batch=b, participant__sex='M', reserve_list=False).count()
        men_wheelchair = BatchParticipant.objects.filter(batch=b, participant__sex='M',
                                                         participant__bear=True, reserve_list=False).count()
        women = BatchParticipant.objects.filter(batch=b, participant__sex='K', reserve_list=False).count()
        women_wheelchair = BatchParticipant.objects.filter(batch=b, participant__sex='K',
                                                           participant__bear=True, reserve_list=False).count()
        if first is True:
            first = False
            item_list += '{"batch": "' + str(b) + '", "men": ' + str(men) + ', "men_wheelchair": ' + str(
                men_wheelchair) + ', "women": ' + str(women) + ', "women_wheelchair": ' + str(women_wheelchair) + '}'
        else:
            item_list += ', {"batch": "' + str(b) + '", "men": ' + str(men) + ', "men_wheelchair": ' + str(
                men_wheelchair) + ', "women": ' + str(women) + ', "women_wheelchair": ' + str(women_wheelchair) + '}'

    item_list += ']'

    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        batch_participants = BatchParticipant.objects.filter(batch__id=kwargs['pk'], reserve_list=False)\
            .order_by('sign_date', 'participant__surname')
        batch_participants_reserve = BatchParticipant.objects.filter(batch__id=kwargs['pk'], reserve_list=True)\
            .order_by('sign_date', 'participant__surname')
        batch_id = kwargs['pk']
        batch = Batch.objects.filter(id=batch_id).first()
        return render(request, template_name, {'batch_participants': batch_participants, 'batch_id': batch_id,
                                               'batch_participants_reserve': batch_participants_reserve, 'now': now,
                                               'item_list': item_list, 'batch': batch})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def batch_view(request, **kwargs):
    template_name = 'homepanel/batch_details.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        batch_details = Batch.objects.filter(id=kwargs['pk']).first()

        summary = BatchParticipant.objects.filter(batch=batch_details).count()
        men = BatchParticipant.objects.filter(batch=batch_details, participant__sex='M').count()
        men_wheelchair = BatchParticipant.objects.filter(batch=batch_details, participant__sex='M',
                                                         participant__bear=True).count()
        women = BatchParticipant.objects.filter(batch=batch_details, participant__sex='K').count()
        women_wheelchair = BatchParticipant.objects.filter(batch=batch_details, participant__sex='K',
                                                           participant__bear=True).count()
        reserve_list = BatchParticipant.objects.filter(batch=batch_details, reserve_list=True).count()
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
                'reserve_list': reserve_list,
                'participant_points': participant_points,
                'volunteer_points': volunteer_points,
            }
        )
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def batch_participant_edit(request, **kwargs):
    form_class = BatchParticipantForm
    template_name = 'homepanel/batch_participant_edit.html'
    batch_participant = BatchParticipant.objects.filter(batch=kwargs['pk'],
                                                        participant=kwargs['batch_participant_id']).first()
    all_rooms = Room.objects.all()
    form = form_class(request.POST or None, instance=batch_participant)
    batch_participant_list = BatchParticipant.objects.filter(participant=kwargs['batch_participant_id'])\
        .order_by('batch_begin_date')
    batches_list = Batch.objects.exclude(batchpar__in=batch_participant_list)
    form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year, end_date__gte=now,
                                                          id__in=batches_list) |
                                     Batch.objects.filter(end_date__year=now.year, end_date__gte=now,
                                                          id__in=batches_list)).distinct().order_by('begin_date')
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            batch_participant.save()
            batch1 = kwargs['pk']
            batch2 = form.cleaned_data['batch']
            batch1.participants -= 1
            batch1.save()
            batch2.participants += 1
            batch2.save()
            batches_list = Batch.objects.exclude(batchpar__in=batch_participant_list)
            form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year, end_date__gte=now,
                                                                  id__in=batches_list) |
                                             Batch.objects.filter(end_date__year=now.year, end_date__gte=now,
                                                                  id__in=batches_list)).distinct()\
                .order_by('begin_date')

            messages.info(request, 'Podopieczny został przepisany.')

            return redirect('homepanel:participants_list', kwargs['pk'])
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'rooms': all_rooms,
                                           'batch_participant': batch_participant})


@login_required
def rooms(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        rooms_list = Room.objects.all().order_by('floor_number', 'number')
        return render(request, 'homepanel/rooms.html', {'rooms_list': rooms_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def all_participants(request):
    template_name = 'homepanel/all_participants.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():

        search_query = request.GET.get('search', '')
        if len(search_query) > 0:
            participants_all = (
                Participant.objects.filter(surname__contains=search_query) |
                Participant.objects.filter(first_name__contains=search_query) |
                Participant.objects.filter(zip_code__contains=search_query)
            ).order_by('surname')
            paginator = Paginator(participants_all, 50)
            page = request.GET.get('page', 1)
        else:
            participants_all = Participant.objects.all().order_by('surname')
            paginator = Paginator(participants_all, 50)
            page = request.GET.get('page', 1)

        try:
            participants_list = paginator.page(page)
        except PageNotAnInteger:
            participants_list = paginator.page(1)
        except EmptyPage:
            participants_list = paginator.page(paginator.num_pages)
        return render(request, template_name, {'participants_list': participants_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def add_participant(request):
    form_class = ParticipantForm
    template_name = 'homepanel/add_participant.html'
    form = form_class(request.POST or None)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save()

            messages.success(request, 'Podopieczny został dodany.')

            return redirect('homepanel:all_participants')
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form})


@login_required
def move_participant_to_base_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        participant = Participant.objects.filter(id=kwargs['participant_id'])
        batch = Batch.objects.filter(id=kwargs['batch_id'])
        batch_participant = BatchParticipant.objects.get(participant=participant, batch=batch)
        batch_participant.reserve_list = False
        batch_participant.save()

        messages.success(request, 'Podopieczny został wpisany na listę podstawową.')

        return HttpResponseRedirect(reverse('homepanel:participant_sign', kwargs={'participant_id': participant.id}))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def edit_participant(request, **kwargs):
    form_class = ParticipantForm
    template_name = 'homepanel/edit_participant.html'
    participant = Participant.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=participant)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            participant.save()

            messages.success(request, 'Dane zostały zapiane.')

            return redirect('homepanel:participant_details', participant.id)
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'participant': participant})


@login_required
def delete_participant(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        query = Participant.objects.get(id=kwargs['pk'])
        query.delete()

        messages.info(request, 'Podopieczny został usunięty.')

        return HttpResponseRedirect(reverse('homepanel:all_participants'))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def participant_sign(request, **kwargs):
    form_class = BatchParticipantForm
    template_name = 'homepanel/participant_sign.html'
    future_batches = (Batch.objects.filter(begin_date__year=now.year, end_date__gte=now) |
                      Batch.objects.filter(begin_date__year=now.year+1, end_date__gte=now)).order_by('begin_date')
    item_list = "["
    first = True

    for b in future_batches:
        men = BatchParticipant.objects.filter(batch=b, participant__sex='M').count()
        men_wheelchair = BatchParticipant.objects.filter(batch=b, participant__sex='M',
                                                         participant__bear=True).count()
        women = BatchParticipant.objects.filter(batch=b, participant__sex='K').count()
        women_wheelchair = BatchParticipant.objects.filter(batch=b, participant__sex='K',
                                                           participant__bear=True).count()
        if first is True:
            first = False
            item_list += '{"batch": "' + str(b) + '", "men": ' + str(men) + ', "men_wheelchair": ' + str(
                men_wheelchair) + ', "women": ' + str(women) + ', "women_wheelchair": ' + str(women_wheelchair) + '}'
        else:
            item_list += ', {"batch": "'+str(b)+'", "men": '+str(men)+', "men_wheelchair": '+str(
                men_wheelchair)+', "women": '+str(women)+', "women_wheelchair": '+str(women_wheelchair)+'}'

    item_list += ']'
    participant = Participant.objects.filter(id=kwargs['participant_id']).first()
    batch_participant_list = BatchParticipant.objects.filter(participant=participant).order_by('-batch__begin_date')
    form = form_class(request.POST or None)
    batches_list = Batch.objects.exclude(batchpar__in=batch_participant_list)
    form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year, end_date__gte=now,
                                                          id__in=batches_list) |
                                     Batch.objects.filter(begin_date__year=now.year+1, end_date__gte=now,
                                                          id__in=batches_list)).distinct().order_by('begin_date')

    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            batch = form.cleaned_data['batch']
            user_exists_in_batch = BatchParticipant.objects.filter(batch=batch, participant=participant).count()
            if user_exists_in_batch == 0:
                batch_participant = form.save(commit=False)
                batch = form.cleaned_data['batch']
                if not batch.name == "Sylwester":
                    batch_participant.batch_begin_date = batch.begin_date + timedelta(days=2) - timedelta(hours=10)
                else:
                    batch_participant.batch_begin_date = batch.begin_date
                batch_participant.batch_end_date = batch.end_date
                batch_participant.participant = participant
                batch_participant.full_cost = batch.batch_price
                batch_participant.payment_id = "#t" + str(batch.id) + "p" + str(participant.id)
                batch_participant.save()
                batch.participants += 1
                batch.save()
                batches_list = Batch.objects.exclude(batchpar__in=batch_participant_list)
                form.fields["batch"].queryset = (Batch.objects.filter(begin_date__year=now.year, end_date__gte=now,
                                                                      id__in=batches_list) |
                                                 Batch.objects.filter(end_date__year=now.year, end_date__gte=now,
                                                                      id__in=batches_list)).distinct()\
                    .order_by('begin_date')

                messages.success(request, 'Podpieczny został zapisany na turnus.')

                return HttpResponseRedirect(
                    reverse('homepanel:participant_sign', kwargs={'participant_id': participant.id}))
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'participant': participant, 'item_list': item_list,
                                           'batch_participant_list': batch_participant_list, 'now': now})


@login_required
def participant_details(request, **kwargs):
    template_name = 'homepanel/participant_details.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        participant = Participant.objects.filter(id=kwargs['pk']).first()
        all_batches = BatchParticipant.objects.filter(participant=participant)
        return render(request, template_name, {'participant': participant, 'all_batches': all_batches})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def all_bookings(request):
    template_name = 'homepanel/all_bookings.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        all_bookings_list = Booking.objects.exclude(room=None).order_by('-begin_date', 'surname')
        paginator = Paginator(all_bookings_list, 15)
        page = request.GET.get('page', 1)
        try:
            booking_list = paginator.page(page)
        except PageNotAnInteger:
            booking_list = paginator.page(1)
        except EmptyPage:
            booking_list = paginator.page(paginator.num_pages)
        return render(request, template_name, {'booking_list': booking_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def all_bookings_meals(request):
    template_name = 'homepanel/all_bookings_meals.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        all_booking_meals_list = Booking.objects.filter(room=None).order_by('-begin_date', 'surname')
        paginator = Paginator(all_booking_meals_list, 15)
        page = request.GET.get('page', 1)
        try:
            booking_meals_list = paginator.page(page)
        except PageNotAnInteger:
            booking_meals_list = paginator.page(1)
        except EmptyPage:
            booking_meals_list = paginator.page(paginator.num_pages)
        return render(request, template_name, {'booking_meals_list': booking_meals_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def delete_booking(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        query = Booking.objects.get(id=kwargs['pk'])
        query.delete()

        messages.info(request, 'Rezerwacja została usunięta.')

        return HttpResponseRedirect(reverse('homepanel:all_bookings'))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def delete_meals_booking(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        query = Booking.objects.get(id=kwargs['pk'])
        query.delete()

        messages.info(request, 'Rezerwacja została usunięta.')

        return HttpResponseRedirect(reverse('homepanel:all_bookings_meals'))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def booking_details(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        template_name = 'homepanel/booking_details.html'
        booking = Booking.objects.filter(id=kwargs['pk']).first()
        return render(request, template_name, {'booking': booking})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def add_booking(request):
    form_class = BookingForm
    template_name = 'homepanel/add_booking.html'
    form = form_class(request.POST or None)
    prices = Price.objects.all()
    rooms_list = Room.objects.all().values('number', 'beds_number')
    rooms_json = json.dumps(list(rooms_list), cls=DjangoJSONEncoder)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            if form.cleaned_data['end_date'] > form.cleaned_data['begin_date'] > now:
                booking = form.save()
                booking_id = booking.id

                return redirect('homepanel:add_booking_2', booking_id)
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'prices': prices, 'rooms_json': rooms_json})


@login_required
def add_booking_2(request, **kwargs):
    form_class = BookingRoomForm
    template_name = 'homepanel/add_booking_2.html'
    booking = Booking.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=booking)
    prices = Price.objects.all()
    rooms_list = Room.objects.all().values('number', 'beds_number')
    rooms_json = json.dumps(list(rooms_list), cls=DjangoJSONEncoder)
    form.fields["room"].queryset = empty_rooms(booking.begin_date, booking.end_date, booking.id)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            room = form.cleaned_data['room']
            booking.room = room
            booking.save()

            admin_email = settings.EMAIL_HOST_USER
            to_email = booking.email_address

            msg = MIMEMultipart('alternative')
            subject = "Rezerwacja nr " + str(booking.id) + " - Dom Rekolekcyjny Brańszczyk"
            msg['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
            msg['From'] = "Centrum Księdza Orione"
            msg['To'] = to_email

            html = render_to_string('homepanel/emails/booking_email.html', {'booking': booking})
            part = MIMEText(html, 'html')
            msg.attach(part)

            fp = open('/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/small-icons.png', 'rb')
            image = MIMEImage(fp.read())
            fp.close()

            fp = open('/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/orione-name.png', 'rb')
            image2 = MIMEImage(fp.read())
            fp.close()

            image.add_header('Content-ID', '<image1>')
            msg.attach(image)
            image2.add_header('Content-ID', '<image2>')
            msg.attach(image2)

            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            mail.sendmail(admin_email, to_email, msg.as_string())
            mail.quit()

            messages.success(request, 'Rezerwacja została zapisana.')

            return redirect('homepanel:all_bookings')
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'prices': prices, 'rooms_json': rooms_json,
                                           'booking': booking})


@login_required
def edit_booking(request, **kwargs):
    form_class = BookingForm
    template_name = 'homepanel/edit_booking.html'
    booking = Booking.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=booking)
    prices = Price.objects.all()
    rooms_list = Room.objects.all().values('number', 'beds_number')
    rooms_json = json.dumps(list(rooms_list), cls=DjangoJSONEncoder)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            if form.cleaned_data['end_date'] > form.cleaned_data['begin_date'] > now:
                form.save(commit=False)
                booking.save()

                return redirect('homepanel:edit_booking_2', booking.id)
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'booking': booking, 'prices': prices,
                                           'rooms_json': rooms_json})


@login_required
def add_booking3(request, **kwargs):
    form_class = BookingForm
    template_name = 'homepanel/edit_booking.html'
    booking = Booking.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=booking)
    prices = Price.objects.all()
    rooms_list = Room.objects.all().values('number', 'beds_number')
    rooms_json = json.dumps(list(rooms_list), cls=DjangoJSONEncoder)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            if form.cleaned_data['end_date'] > form.cleaned_data['begin_date'] > now:
                form.save(commit=False)
                booking.save()

                return redirect('homepanel:add_booking_2', booking.id)
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'booking': booking, 'prices': prices,
                                           'rooms_json': rooms_json})


@login_required
def edit_booking_2(request, **kwargs):
    form_class = BookingRoomForm
    template_name = 'homepanel/edit_booking_2.html'
    booking = Booking.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=booking)
    prices = Price.objects.all()
    rooms_list = Room.objects.all().values('number', 'beds_number')
    rooms_json = json.dumps(list(rooms_list), cls=DjangoJSONEncoder)
    form.fields["room"].queryset = empty_rooms(booking.begin_date, booking.end_date, booking.id)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            room = form.cleaned_data['room']
            booking.room = room
            booking.save()

            admin_email = settings.EMAIL_HOST_USER
            to_email = booking.email_address

            msg = MIMEMultipart('alternative')
            subject = "Zmiana rezerwacji nr " + str(booking.id) + " - Dom Rekolekcyjny Brańszczyk"
            msg['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
            msg['From'] = "Centrum Księdza Orione"
            msg['To'] = to_email

            html = render_to_string('homepanel/emails/booking_edit_email.html', {'booking': booking})
            part = MIMEText(html, 'html')
            msg.attach(part)

            fp = open('/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/small-icons.png',
                      'rb')
            image = MIMEImage(fp.read())
            fp.close()

            fp = open('/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/orione-name.png',
                      'rb')
            image2 = MIMEImage(fp.read())
            fp.close()

            image.add_header('Content-ID', '<image1>')
            msg.attach(image)
            image2.add_header('Content-ID', '<image2>')
            msg.attach(image2)

            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            mail.sendmail(admin_email, to_email, msg.as_string())
            mail.quit()

            messages.success(request, 'Rezerwacja została zapisana.')

            return redirect('homepanel:booking_details', booking.id)
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'booking': booking, 'prices': prices,
                                           'rooms_json': rooms_json})


@login_required
def participant_payment(request, **kwargs):
    form_class = PaymentForm
    template_name = 'homepanel/participant_payment.html'
    batch_participant = BatchParticipant.objects.filter(batch=kwargs['batch_id'],
                                                        participant=kwargs['participant_id']).first()
    form = form_class(request.POST or None, instance=batch_participant)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            batch_participant.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('homepanel:participant_sign', batch_participant.participant_id)
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'batch_participant': batch_participant})


@login_required
def batch_participant_delete(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        query = BatchParticipant.objects.get(batch=kwargs['batch_id'], participant=kwargs['participant_id'])
        participant_id = query.participant.id
        batch = query.batch
        batch.participants -= 1
        batch.save()
        query.delete()

        messages.info(request, 'Podopieczny został wypisany z turnusu.')

        return HttpResponseRedirect(reverse('homepanel:participant_sign', kwargs={'participant_id': participant_id}))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def booking_payment(request, **kwargs):
    form_class = BookingPaymentForm
    template_name = 'homepanel/booking_payment.html'
    booking = Booking.objects.filter(id=kwargs['booking_id']).first()
    form = form_class(request.POST or None, instance=booking)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            booking.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('homepanel:all_bookings')
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'booking': booking})


@login_required
def add_meals_booking(request):
    form_class = BookingMealsForm
    template_name = 'homepanel/add_meals_booking.html'
    form = form_class(request.POST or None)
    prices = Price.objects.all()
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            if form.cleaned_data['end_date'] > form.cleaned_data['begin_date'] > now:
                booking = form.save()

                admin_email = settings.EMAIL_HOST_USER
                to_email = booking.email_address

                msg = MIMEMultipart('alternative')
                subject = "Rezerwacja nr " + str(booking.id) + " - Dom Rekolekcyjny Brańszczyk"
                msg['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
                msg['From'] = "Centrum Księdza Orione"
                msg['To'] = to_email

                html = render_to_string('homepanel/emails/meals_booking_email.html', {'booking': booking})
                part = MIMEText(html, 'html')
                msg.attach(part)

                fp = open(
                    '/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/small-icons.png',
                    'rb')
                image = MIMEImage(fp.read())
                fp.close()

                fp = open(
                    '/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/orione-name.png',
                    'rb')
                image2 = MIMEImage(fp.read())
                fp.close()

                image.add_header('Content-ID', '<image1>')
                msg.attach(image)
                image2.add_header('Content-ID', '<image2>')
                msg.attach(image2)

                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                mail.sendmail(admin_email, to_email, msg.as_string())
                mail.quit()

                messages.success(request, 'Rezerwacja została zapisana.')

                return redirect('homepanel:all_bookings_meals')
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'prices': prices})


@login_required
def edit_meals_booking(request, **kwargs):
    form_class = BookingMealsForm
    template_name = 'homepanel/edit_meals_booking.html'
    booking = Booking.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, instance=booking)
    prices = Price.objects.all()
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        if request.POST and form.is_valid():
            if form.cleaned_data['end_date'] > form.cleaned_data['begin_date'] > now:
                form.save(commit=False)
                booking = form.save()

                admin_email = settings.EMAIL_HOST_USER
                to_email = booking.email_address

                msg = MIMEMultipart('alternative')
                subject = "Zmiana rezerwacji nr " + str(booking.id) + " - Dom Rekolekcyjny Brańszczyk"
                msg['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
                msg['From'] = "Centrum Księdza Orione"
                msg['To'] = to_email

                html = render_to_string('homepanel/emails/meals_booking_edit_email.html', {'booking': booking})
                part = MIMEText(html, 'html')
                msg.attach(part)

                fp = open(
                    '/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/small-icons.png',
                    'rb')
                image = MIMEImage(fp.read())
                fp.close()

                fp = open(
                    '/home/drabinajakuba/websites/engineeringwork/drabinajakubowa/static/images/orione-name.png',
                    'rb')
                image2 = MIMEImage(fp.read())
                fp.close()

                image.add_header('Content-ID', '<image1>')
                msg.attach(image)
                image2.add_header('Content-ID', '<image2>')
                msg.attach(image2)

                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                mail.sendmail(admin_email, to_email, msg.as_string())
                mail.quit()

                messages.success(request, 'Rezerwacja została zapisana.')

                return redirect('homepanel:booking_details', booking.id)
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'booking': booking, 'prices': prices})


@login_required
def certificates(request):
    template_name = 'homepanel/certificates.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        certificates_list = BatchVolunteer.objects.all().values('volunteer__first_name', 'volunteer__surname',
                                                                'batch__name', 'batch__institution__city',
                                                                'batch_begin_date', 'batch_end_date', 'batch_days',
                                                                'nights', 'training_days', 'batch__training_duration',
                                                                'unique_key')
        participant_certificates_list = BatchParticipant.objects.all().values('participant__first_name',
                                                                              'participant__surname', 'batch__name',
                                                                              'batch__institution__city',
                                                                              'batch__begin_date', 'batch__end_date',
                                                                              'unique_key')
        certificates_json = json.dumps(list(certificates_list), cls=DjangoJSONEncoder)
        participant_certificates_json = json.dumps(list(participant_certificates_list), cls=DjangoJSONEncoder)
        return render(request, template_name, {'certificates_json': certificates_json,
                                               'participant_certificates_json': participant_certificates_json})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def event_participant_sign(request, **kwargs):
    form_class = EventParticipantForm
    template_name = 'homepanel/event_participant_sign.html'
    participant = Participant.objects.filter(id=kwargs['participant_id']).first()
    event_participant_list = EventParticipant.objects.filter(participant=participant).order_by('-event__begin_date')
    form = form_class(request.POST or None)
    events_list = Event.objects.exclude(evpartic__in=event_participant_list)
    form.fields["event"].queryset = (Event.objects.filter(begin_date__year=now.year, end_date__gte=now,
                                                          id__in=events_list) |
                                     Event.objects.filter(end_date__year=now.year, end_date__gte=now,
                                                          id__in=events_list)).distinct().order_by('begin_date')
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            event = form.cleaned_data['event']
            user_exists_in_event = EventParticipant.objects.filter(event=event, participant=participant).count()
            if user_exists_in_event == 0:
                event_participant = form.save(commit=False)
                event = form.cleaned_data['event']
                event_participant.participant = participant
                event_participant.total_cost = event.price
                event_participant.payment_id = "#wy" + str(event.id) + "p" + str(participant.id)
                event_participant.save()
                event.participants += 1
                event.save()
                events_list = Event.objects.exclude(evpartic__in=event_participant_list)
                form.fields["event"].queryset = (Event.objects.filter(begin_date__year=now.year, end_date__gte=now,
                                                                      id__in=events_list) |
                                                 Event.objects.filter(end_date__year=now.year, end_date__gte=now,
                                                                      id__in=events_list)).distinct()\
                    .order_by('begin_date')

                messages.success(request, 'Podopieczny został zapisany na wydarzenie.')

                return HttpResponseRedirect(
                    reverse('homepanel:event_participant_sign', kwargs={'participant_id': participant.id}))
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'participant': participant,
                                           'event_participant_list': event_participant_list, 'now': now})


@login_required
def event_participant_delete(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        query = EventParticipant.objects.get(id=kwargs['event_participant_id'])
        participant_id = query.participant.id
        event = query.event
        event.participants -= 1
        event.save()
        query.delete()

        messages.info(request, 'Podopieczny został wypisany z wydarzenia.')

        return HttpResponseRedirect(reverse('homepanel:event_participant_sign', kwargs={'participant_id': participant_id
                                                                                        }))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def from_event_participant_delete(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        query = EventParticipant.objects.get(id=kwargs['event_participant_id'])
        event = query.event
        event.participants -= 1
        event.save()
        query.delete()

        messages.info(request, 'Podopieczny został wypisany z wydarzenia.')

        return HttpResponseRedirect(reverse('homepanel:event_participants', kwargs={'pk': event.id}))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def event_volunteer_delete(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        query = EventVolunteer.objects.get(id=kwargs['event_volunteer_id'])
        event = query.event
        event.volunteers -= 1
        event.save()
        query.delete()

        messages.info(request, 'Wolontariusz został wypisany z wydarzenia.')

        return HttpResponseRedirect(reverse('homepanel:event_volunteers', kwargs={'pk': event.id}))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def retreat_person_delete(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        query = RetreatOrMusicTrainingPerson.objects.get(id=kwargs['training_person_id'])
        retreat = query.retreat_or_music_training
        retreat.people -= 1
        retreat.save()
        query.delete()

        messages.info(request, 'Uczestnik został wypisany z warsztatów/rekolekcji.')

        return HttpResponseRedirect(reverse('homepanel:training_people', kwargs={'pk': retreat.id}))
    else:
        return redirect('homepanel:home_coordinator_login')


class CertificatePDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'homepanel/certificate/participant-certificate.html'
    download_filename = 'certificate.pdf'
    model = BatchParticipant

    def get_object(self, queryset=None):
        obj = BatchParticipant.objects.filter(unique_key=self.kwargs["id"]).first()
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


@login_required
def events(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        events_all = Event.objects.all().order_by('-begin_date')
        paginator = Paginator(events_all, 15)
        page = request.GET.get('page', 1)
        try:
            events_list = paginator.page(page)
        except PageNotAnInteger:
            events_list = paginator.page(1)
        except EmptyPage:
            events_list = paginator.page(paginator.num_pages)
        return render(request, 'homepanel/events.html', {'events_list': events_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def retreats_and_trainings(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        training_all = RetreatOrMusicTraining.objects.all().order_by('-begin_date')
        paginator = Paginator(training_all, 15)
        page = request.GET.get('page', 1)
        try:
            trainings_list = paginator.page(page)
        except PageNotAnInteger:
            trainings_list = paginator.page(1)
        except EmptyPage:
            trainings_list = paginator.page(paginator.num_pages)
        return render(request, 'homepanel/retreats_and_trainings.html', {'trainings_list': trainings_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def event_details(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        template_name = 'homepanel/event_details.html'
        event = Event.objects.filter(id=kwargs['pk']).first()
        return render(request, template_name, {'event': event})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def event_volunteers(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        template_name = 'homepanel/event_volunteers.html'
        event = Event.objects.filter(id=kwargs['pk']).first()
        volunteers_list = EventVolunteer.objects.filter(event=event)
        return render(request, template_name, {'event': event, 'volunteers_list': volunteers_list, 'now': now})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def event_participants(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        template_name = 'homepanel/event_participants.html'
        event = Event.objects.filter(id=kwargs['pk']).first()
        participants_list = EventParticipant.objects.filter(event=event)
        return render(request, template_name, {'event': event, 'participants_list': participants_list, 'now': now})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def training_details(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        template_name = 'homepanel/training_details.html'
        training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
        return render(request, template_name, {'training': training})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def training_people(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        template_name = 'homepanel/training_people.html'
        training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
        training_people_list = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=training)
        return render(request, template_name, {'training': training, 'training_people_list': training_people_list,
                                               'now': now})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def person_details(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        training = RetreatOrMusicTraining.objects.filter(id=kwargs['pk']).first()
        training_person = RetreatOrMusicTrainingPerson.objects.filter(person__id=kwargs['person_id'],
                                                                      retreat_or_music_training=training).first()
        return render(request, 'homepanel/person.html', {'training': training, 'training_person': training_person})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def person_payment(request, **kwargs):
    form_class = PersonPaymentForm
    template_name = 'homepanel/person_payment.html'
    training_person = RetreatOrMusicTrainingPerson.objects.filter(id=kwargs['training_person_id']).first()
    form = form_class(request.POST or None, instance=training_person)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            training_person.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('homepanel:training_people', kwargs['pk'])
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'training_person': training_person})


@login_required
def event_volunteer_payment(request, **kwargs):
    form_class = EventVolunteerPaymentForm
    template_name = 'homepanel/event_volunteer_payment.html'
    event_volunteer = EventVolunteer.objects.filter(id=kwargs['event_volunteer_id']).first()
    form = form_class(request.POST or None, instance=event_volunteer)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            event_volunteer.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('homepanel:event_volunteers', kwargs['pk'])
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'event_volunteer': event_volunteer})


@login_required
def from_event_participant_payment(request, **kwargs):
    form_class = EventParticipantPaymentForm
    template_name = 'homepanel/event_participant_payment.html'
    event_participant = EventParticipant.objects.filter(id=kwargs['event_participant_id']).first()
    form = form_class(request.POST or None, instance=event_participant)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            event_participant.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('homepanel:event_participants', kwargs['pk'])
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'event_participant': event_participant})


@login_required
def event_participant_payment(request, **kwargs):
    form_class = EventParticipantPaymentForm
    template_name = 'homepanel/event_participant_payment.html'
    event_participant = EventParticipant.objects.filter(id=kwargs['event_participant_id']).first()
    form = form_class(request.POST or None, instance=event_participant)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            event_participant.save()

            messages.success(request, 'Płatność została zapisana.')

            return redirect('homepanel:event_participant_sign', kwargs['participant_id'])
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'event_participant': event_participant})


@login_required
def calendar(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        bookings = Booking.objects.filter(begin_date__month=now.month, begin_date__year=now.year) | \
            Booking.objects.filter(end_date__month=now.month, begin_date__year=now.year)
        batches_list = Batch.objects.filter(begin_date__month=now.month, begin_date__year=now.year) | \
            Batch.objects.filter(end_date__month=now.month, begin_date__year=now.year)
        events = Event.objects.filter(begin_date__month=now.month, begin_date__year=now.year) | \
            Event.objects.filter(end_date__month=now.month, begin_date__year=now.year)
        trainings = RetreatOrMusicTraining.objects.filter(begin_date__month=now.month, begin_date__year=now.year) | \
            RetreatOrMusicTraining.objects.filter(end_date__month=now.month, begin_date__year=now.year)
        first = now - timedelta(days=now.day-1)
        month = now.month
        num_list = [6, 13, 20, 27]
        if month in [1, 3, 5, 7, 8, 10, 12]:
            days = 31
        elif month == 2:
            days = 29
        else:
            days = 30

        next = now + timedelta(days=days)

        bookings_next = Booking.objects.filter(begin_date__month=next.month, begin_date__year=next.year) | \
            Booking.objects.filter(end_date__month=next.month, begin_date__year=next.year)
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

        return render(request, 'homepanel/calendar.html', {'events': events, 'now': now, 'days': range(days),
                                                           'num_list': num_list, 'first': first,
                                                           'trainings': trainings, 'batches': batches_list,
                                                           'next': next, 'batches_list_next': batches_list_next,
                                                           'events_next': events_next, 'first_next': first_next,
                                                           'trainings_next': trainings_next,
                                                           'days_next': range(days_next), 'bookings': bookings,
                                                           'bookings_next': bookings_next})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def move_participant_to_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        participant = Participant.objects.filter(id=kwargs['participant_id']).first()
        batch = Batch.objects.filter(id=kwargs['batch_id']).first()
        batch_participant = BatchParticipant.objects.get(participant=participant, batch=batch)
        batch_participant.reserve_list = False
        batch_participant.save()

        messages.success(request, 'Podopieczny został wpisany na listę podstawową.')

        return HttpResponseRedirect(reverse('homepanel:participant_sign', kwargs={'participant_id': participant.id}))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def move_participant_to_base_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        participant = Participant.objects.filter(id=kwargs['participant_id'])
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        batch_participant = BatchParticipant.objects.get(participant=participant, batch=batch)
        batch_participant.reserve_list = False
        batch_participant.save()

        messages.success(request, 'Podopieczny został wpisany na listę podstawową.')

        return HttpResponseRedirect(reverse('homepanel:participants_list', kwargs={'pk': batch.id}))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def move_participant_to_reserve_list(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        participant = Participant.objects.filter(id=kwargs['participant_id'])
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        batch_participant = BatchParticipant.objects.get(participant=participant, batch=batch)
        batch_participant.reserve_list = True
        batch_participant.save()

        messages.success(request, 'Podopieczny został wpisany na listę rezerwową.')

        return HttpResponseRedirect(reverse('homepanel:participants_list', kwargs={'pk': batch.id}))
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def get_participants_from_csv(request):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        with open('test - podopieczni.csv', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_line = True
            for row in reader:
                if first_line:
                    first_line = False
                    continue

                sex = 'M'
                if row[26] == "Kobieta":
                    sex = 'K'

                mental_disability = False
                not_need_help = False
                wheelchair = False
                disabled_hands = False
                crutches = False
                disabled_sight = False
                disabled_hearing = False
                epilepsy = False

                if 'Niepełnosprawność intelektualna' in row[24]:
                    mental_disability = True
                if 'Nie wymaga pomocy' in row[24]:
                    not_need_help = True
                if 'Porusza się na wózku' in row[24]:
                    wheelchair = True
                if 'Niesprawne ręce' in row[24]:
                    disabled_hands = True
                if 'Porusza się o kulach' in row[24]:
                    crutches = True
                if 'Niesprawny wzrok' in row[24]:
                    disabled_sight = True
                if 'Niesprawny słuch' in row[24]:
                    disabled_hearing = True
                if 'Możliwe ataki padaczki' in row[24]:
                    epilepsy = True

                how_know = 'I'
                if row[16] == 'Od znajomych wolontariuszy':
                    how_know = 'Z'
                elif row[16] == 'Od znajomych podopiecznych':
                    how_know = 'P'
                elif row[16] == 'Z kościoła':
                    how_know = 'K'
                elif row[16] == 'Ze spotkania w moim duszpasterstwie':
                    how_know = 'D'
                elif row[16] == 'Z Anielskiej Domówki':
                    how_know = 'AD'
                elif row[16] == 'Z uczelni lub ze szkoły':
                    how_know = 'US'
                elif row[16] == 'Z Facebooka':
                    how_know = 'FB'
                elif row[16] == 'Z radia, TV, prasy':
                    how_know = 'TV'
                elif row[16] == 'Z tej strony internetowej':
                    how_know = 'S'
                elif row[16] == 'Z filmu na YouTube':
                    how_know = 'YT'

                first_time = False
                if row[18] == 'Tak':
                    first_time = True

                drugs = 'N'
                if row[21] == 'Tak':
                    drugs = 'T'
                elif row[21] == 'Brak danych':
                    drugs = 'BD'

                communication = 'N'
                if "Podopieczny nie ma problemu z komunikacją" in row[19]:
                    communication = 'OK'
                elif 'Podopieczny komunikuje się z trudem' in row[19]:
                    communication = 'TR'
                elif 'Podopieczny korzysta z książki do komunikacji' in row[19]:
                    communication = 'KS'
                elif 'Podopieczny komunikuje się przy pomocy języka migowego' in row[19]:
                    communication = 'MI'

                participant = Participant.objects.create(
                    first_name=row[5],
                    surname=row[4],
                    pesel=row[6],
                    sex=sex,
                    phone_number=row[11],
                    guardian_name=row[12],
                    guardian_phone_number=row[13],
                    email_address=row[14],
                    city=row[10],
                    zip_code=row[9],
                    address=row[8],
                    flower=communication,
                    others=row[20],
                    foundation=row[15],
                    how_know_dj=how_know,
                    is_first_time=first_time,
                    candies=drugs,
                    cat=mental_disability,
                    dog=not_need_help,
                    bear=wheelchair,
                    monkey=disabled_hands,
                    frog=crutches,
                    bat=disabled_sight,
                    spider=disabled_hearing,
                    fish=epilepsy
                )

                batch = Batch.objects.filter(id=6).first()     # 5
                if row[17] == 'Sylwester':
                    batch = Batch.objects.filter(id=1).first()  # s
                elif row[17] == 'Brańszczyk1':
                    batch = Batch.objects.filter(id=2).first()  # 1
                elif row[17] == 'Brańszczyk2':
                    batch = Batch.objects.filter(id=3).first()  # 2
                elif row[17] == 'Brańszczyk3':
                    batch = Batch.objects.filter(id=4).first()  # 3
                elif row[17] == 'Brańszczyk4':
                    batch = Batch.objects.filter(id=5).first()  # 4

                reserve_list = False
                if row[23] == 'Tak':
                    reserve_list = True

                installment = 0
                part_paid = False
                if len(row[22]) > 0:
                    installment = float(row[22][:3])
                    part_paid = True

                if row[17] == 'Sylwester':
                    BatchParticipant.objects.create(
                        participant=participant,
                        batch=batch,
                        batch_begin_date=batch.begin_date,
                        batch_end_date=batch.end_date,
                        reserve_list=reserve_list,
                        full_cost=batch.batch_price,
                        installment=installment,
                        is_part_paid=part_paid
                    )
                else:
                    BatchParticipant.objects.get_or_create(
                        participant=participant,
                        batch=batch,
                        batch_begin_date=batch.begin_date+timedelta(2),
                        batch_end_date=batch.end_date,
                        reserve_list=reserve_list,
                        full_cost=batch.batch_price,
                        installment=installment,
                        is_part_paid=part_paid
                    )
        return redirect('homepanel:all_participants')
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def export_participants_to_csv(request):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="participants.csv"'

        participants = Participant.objects.order_by('surname')
        rows = []

        for participant in participants:
            person = [
                participant.surname,
                participant.first_name,
                participant.address,
                participant.city,
                participant.zip_code,
                participant.email_address
            ]
            rows.append(person)

        csv.register_dialect(
            'myDialect', delimiter=';', quoting=csv.QUOTE_ALL, skipinitialspace=True, lineterminator='\r'
        )

        writer = csv.writer(response, dialect='myDialect')
        for row in rows:
            writer.writerow(row)

        return response
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def update_participants_count(request):
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        batches_year = Batch.objects.filter(begin_date__year=now.year) | Batch.objects.filter(end_date__year=now.year)
        for batch in batches_year:
            all_participants_on_batch = BatchParticipant.objects.filter(batch=batch).count()
            all_volunteers_on_batch = BatchVolunteer.objects.filter(batch=batch).count()
            batch.participants = all_participants_on_batch
            batch.volunteers = all_volunteers_on_batch
            batch.save()
        return redirect('homepanel:all_participants')
    else:
        return redirect('homepanel:home_coordinator_login')


class LetterPDFView(PDFTemplateResponseMixin, DetailView):
    template_name = 'homepanel/certificate/participant-letter.html'
    download_filename = 'letter.pdf'
    model = BatchParticipant

    def get_object(self, queryset=None):
        obj = BatchParticipant.objects.filter(unique_key=self.kwargs["id"]).first()
        if obj:
            return obj
        return None

    def get_context_data(self, **kwargs):
        return super(LetterPDFView, self).get_context_data(
            pagesize='A4',
            title='List potwierdzający',
            congregation=Congregation.objects.first(),
            home=Home.objects.first(),
            heaven_gate=Event.objects.filter(begin_date__year=now.year, name="Brama Nieba").first(),
            central_dj=Event.objects.filter(begin_date__year=now.year, name="Sztab Centralny").first(),
            date=now,
            **kwargs
        )


@login_required
def export_email_addresses_to_csv(request):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="email_addresses.csv"'

        batch_participants = BatchParticipant.objects.order_by('batch')
        batch_volunteers = BatchVolunteer.objects.order_by('batch')
        event_participants = EventParticipant.objects.order_by('event')
        event_volunteers = EventVolunteer.objects.order_by('event')
        workshop_people = RetreatOrMusicTrainingPerson.objects.order_by('retreat_or_music_training')
        all_participants = Participant.objects.order_by('surname')
        all_volunteers = Volunteer.objects.order_by('surname')

        addresses = []

        for batch_part in batch_participants:
            person = [str(batch_part.participant), batch_part.participant.email_address, str(batch_part.batch)]
            addresses.append(person)

        for event_part in event_participants:
            person = [str(event_part.participant), event_part.participant.email_address, str(event_part.event)]
            addresses.append(person)

        for batch_vol in batch_volunteers:
            person = [str(batch_vol.volunteer), batch_vol.volunteer.email_address, str(batch_vol.batch)]
            addresses.append(person)

        for event_vol in event_volunteers:
            person = [str(event_vol.volunteer), event_vol.volunteer.email_address, str(event_vol.event)]
            addresses.append(person)

        for workshop_person in workshop_people:
            person = [str(workshop_person.person), workshop_person.person.email_address,
                      str(workshop_person.retreat_or_music_training)]
            addresses.append(person)

        for participant in all_participants:
            person = [str(participant), participant.email_address, 'Podopieczni']
            addresses.append(person)

        for volunteer in all_volunteers:
            person = [str(volunteer), volunteer.email_address, 'Wolontariusze']
            addresses.append(person)

        csv.register_dialect('myDialect',
                             delimiter=';',
                             quoting=csv.QUOTE_ALL,
                             skipinitialspace=True,
                             lineterminator='\r')

        writer = csv.writer(response, dialect='myDialect')
        for row in addresses:
            writer.writerow(row)

        return response
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def export_data_to_xlsx(request):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():

        all_volunteers = Volunteer.objects.order_by('surname')

        number = []
        pesel = []
        surname = []
        family_list = []
        first_name = []
        father_list = []
        mother_list = []
        date_of_birth = []

        for index, volunteer in enumerate(all_volunteers):
            mother = volunteer.mother_first_name
            father = volunteer.father_first_name
            family = volunteer.family_name
            name = volunteer.first_name
            if len(name.split()) > 2:
                name = name[0]
            if mother is None:
                mother = "brak danych"
            if father is None:
                father = "brak danych"
            if family is None:
                family = volunteer.surname
            number.append(str(index + 1))
            pesel.append(volunteer.pesel)
            surname.append(volunteer.surname)
            family_list.append(family)
            first_name.append(name)
            father_list.append(father)
            mother_list.append(mother)
            date_of_birth.append(get_date_of_birth(volunteer.pesel))

        df = pandas.DataFrame({'Lp.': number, 'PESEL': pesel, 'Nazwisko': surname, 'Nazwisko rodowe': family_list,
                               'Pierwsze imię': first_name, 'Imię ojca': father_list, 'Imię matki': mother_list,
                               'Data urodzenia': date_of_birth})
        df.to_excel("data.xlsx", sheet_name='Sheet', index=False, columns=['Lp.', 'PESEL', 'Nazwisko',
                                                                           'Nazwisko rodowe', 'Pierwsze imię',
                                                                           'Imię ojca', 'Imię matki', 'Data urodzenia'])

        excel = open("data.xlsx", "rb")
        response = HttpResponse(excel, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
        return response
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def batch_export_data_to_xlsx(request, **kwargs):
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists():
        batch = Batch.objects.filter(id=kwargs['pk']).first()
        all_batch_volunteers = BatchVolunteer.objects.filter(batch=batch).order_by('volunteer__surname')

        number = []
        pesel = []
        surname = []
        family_list = []
        first_name = []
        father_list = []
        mother_list = []
        date_of_birth = []

        for index, bv in enumerate(all_batch_volunteers):
            mother = bv.volunteer.mother_first_name
            father = bv.volunteer.father_first_name
            family = bv.volunteer.family_name
            name = bv.volunteer.first_name
            if len(name.split()) > 2:
                name = name[0]
            if mother is None:
                mother = "brak danych"
            if father is None:
                father = "brak danych"
            if family is None:
                family = bv.volunteer.surname
            number.append(str(index + 1))
            pesel.append(bv.volunteer.pesel)
            surname.append(bv.volunteer.surname)
            family_list.append(family)
            first_name.append(name)
            father_list.append(father)
            mother_list.append(mother)
            date_of_birth.append(get_date_of_birth(bv.volunteer.pesel))

        df = pandas.DataFrame({'Lp.': number, 'PESEL': pesel, 'Nazwisko': surname, 'Nazwisko rodowe': family_list,
                               'Pierwsze imię': first_name, 'Imię ojca': father_list, 'Imię matki': mother_list,
                               'Data urodzenia': date_of_birth})
        df.to_excel("data.xlsx", sheet_name='Sheet', index=False, columns=['Lp.', 'PESEL', 'Nazwisko',
                                                                           'Nazwisko rodowe', 'Pierwsze imię',
                                                                           'Imię ojca', 'Imię matki', 'Data urodzenia'])

        excel = open("data.xlsx", "rb")
        response = HttpResponse(excel, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
        return response
    else:
        return redirect('homepanel:home_coordinator_login')


def get_date_of_birth(pesel):
    yy = pesel[0:2]
    mm = pesel[2:4]
    dd = pesel[4:6]
    if int(mm) > 12:
        yy = "20" + yy
        mm = int(mm) - 20
    else:
        yy = "19" + yy

    if 0 < int(mm) <= 12 and 0 < int(dd) <= 31:
        birthday = datetime.strptime(str(yy) + " " + str(mm) + " " + str(dd), '%Y %m %d')
        birthday = birthday.strftime("%Y.%m.%d")
    else:
        birthday = 'err'
    return birthday


@login_required
def participant_photo_edit(request, **kwargs):
    form_class = SetParticipantPhotoForm
    template_name = 'homepanel/participant_photo_edit.html'
    participant = Participant.objects.filter(id=kwargs['pk']).first()
    form = form_class(request.POST or None, request.FILES, instance=participant)
    if request.user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            request.user.groups.filter(name='Koordynatorzy zapisów').exists():
        if request.POST and form.is_valid():
            form.save(commit=False)
            participant.save()

            messages.success(request, 'Zdjęcie zostało zaktualizowane.')

            return render(request, 'homepanel/participant_details.html', {'participant': participant})
    else:
        return redirect('homepanel:home_coordinator_login')

    return render(request, template_name, {'form': form, 'participant': participant})


@login_required
def all_volunteers(request):
    template_name = 'homepanel/all_volunteers.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():

        search_query = request.GET.get('search', '')
        if len(search_query) > 0:
            volunteers_all = (Volunteer.objects.filter(surname__contains=search_query) |
                              Volunteer.objects.filter(first_name__contains=search_query)).order_by('surname')
            paginator = Paginator(volunteers_all, 50)
            page = request.GET.get('page', 1)
        else:
            volunteers_all = Volunteer.objects.all().order_by('surname')
            paginator = Paginator(volunteers_all, 50)
            page = request.GET.get('page', 1)

        try:
            volunteers_list = paginator.page(page)
        except PageNotAnInteger:
            volunteers_list = paginator.page(1)
        except EmptyPage:
            volunteers_list = paginator.page(paginator.num_pages)
        return render(request, template_name, {'volunteers_list': volunteers_list})
    else:
        return redirect('homepanel:home_coordinator_login')


@login_required
def volunteer_details(request, **kwargs):
    template_name = 'homepanel/volunteer_details.html'
    user = request.user
    if user.groups.filter(name__in=['Koordynatorzy domu']).exists() or \
            user.groups.filter(name='Koordynatorzy zapisów').exists():
        volunteer = Volunteer.objects.filter(id=kwargs['pk']).first()
        all_batches = BatchVolunteer.objects.filter(volunteer=volunteer)
        all_events = EventVolunteer.objects.filter(volunteer=volunteer)
        all_retreats_and_trainings = RetreatOrMusicTrainingPerson.objects.filter(volunteer=volunteer)
        return render(request, template_name, {'volunteer': volunteer, 'all_batches': all_batches,
                                               'all_events': all_events,
                                               'all_retreats_and_trainings': all_retreats_and_trainings})
    else:
        return redirect('homepanel:home_coordinator_login')
