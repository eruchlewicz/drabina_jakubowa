from django.conf.urls import url
from . import views
from .views import *
from django.contrib.auth.decorators import login_required

app_name = 'homepanel'
urlpatterns = [
    url(r'^logowanie/$', views.home_coordinator_login, name='home_coordinator_login'),
    url(r'^wylogowanie/$', views.logout_view, name='logout'),
    url(r'^kalendarz/$', views.calendar, name='calendar'),
    url(r'^turnus/(?P<pk>[0-9]+)/$', views.batch_view, name='batch_view'),
    url(r'^turnus/(?P<pk>[0-9]+)/wolontariusze/$', views.volunteers, name='volunteers_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/$', views.participants, name='participants_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<participant_id>[0-9]+)/wpisz/$',
        views.move_participant_to_base_list, name='move_participant_to_base_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<participant_id>[0-9]+)/rezerwowa/$',
        views.move_participant_to_reserve_list, name='move_participant_to_reserve_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<id>[\w{}.-]{1,36})/zaswiadczenie.pdf/$',
        login_required(CertificatePDFView.as_view()), name='certificate'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<id>[\w{}.-]{1,36})/list.pdf/$',
        login_required(LetterPDFView.as_view()), name='letter'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<batch_participant_id>[0-9]+)/$', views.batch_participant_edit,
        name='batch_participant_edit'),
    url(r'^turnusy/$', views.batches, name='batches'),
    url(r'^wydarzenia/$', views.events, name='events'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/$', views.event_details, name='event_details'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/wolontariusze/$', views.event_volunteers, name='event_volunteers'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/wolontariusze/(?P<event_volunteer_id>[0-9]+)/platnosci/$',
        views.event_volunteer_payment, name='event_volunteer_payment'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/wolontariusze/(?P<event_volunteer_id>[0-9]+)/usun/$',
        views.event_volunteer_delete, name='event_volunteer_delete'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/podopieczni/$', views.event_participants, name='event_participants'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/podopieczni/(?P<event_participant_id>[0-9]+)/platnosci/$',
        views.from_event_participant_payment, name='from_event_participant_payment'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/podopieczni/(?P<event_participant_id>[0-9]+)/usun/$',
        views.from_event_participant_delete, name='from_event_participant_delete'),
    url(r'^warsztaty-i-rekolekcje/$', views.retreats_and_trainings, name='retreats_and_trainings'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/$', views.training_details, name='training_details'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/$', views.training_people, name='training_people'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/(?P<person_id>[0-9]+)/$', views.person_details,
        name='person_details'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/(?P<training_person_id>[0-9]+)/platnosci/$',
        views.person_payment, name='person_payment'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/(?P<training_person_id>[0-9]+)/usun/$',
        views.retreat_person_delete, name='retreat_person_delete'),
    url(r'^pokoje/$', views.rooms, name='rooms'),
    url(r'^zaswiadczenia/$', views.certificates, name='certificates'),
    url(r'^podopieczni/$', views.all_participants, name='all_participants'),
    url(r'^podopieczni/dodaj/$', views.add_participant, name='add_participant'),
    url(r'^podopieczni/(?P<pk>[0-9]+)/$', views.participant_details, name='participant_details'),
    url(r'^podopieczni/(?P<participant_id>[0-9]+)/turnusy/$', views.participant_sign, name='participant_sign'),
    url(r'^podopieczni/(?P<participant_id>[0-9]+)/wydarzenia/$', views.event_participant_sign,
        name='event_participant_sign'),
    url(r'^podopieczni/(?P<participant_id>[0-9]+)/wydarzenia/(?P<event_participant_id>[0-9]+)/usun/$',
        views.event_participant_delete, name='event_participant_delete'),
    url(r'^podopieczni/(?P<participant_id>[0-9]+)/wydarzenia/(?P<event_participant_id>[0-9]+)/platnosci/$',
        views.event_participant_payment, name='event_participant_payment'),
    url(r'^podopieczni/(?P<participant_id>[0-9]+)/turnusy/(?P<batch_id>[0-9]+)/platnosci/$', views.participant_payment,
        name='participant_payment'),
    url(r'^podopieczni/(?P<participant_id>[0-9]+)/turnusy/(?P<batch_id>[0-9]+)/wpisz/$',
        views.move_participant_to_list, name='move_participant_to_list'),
    url(r'^podopieczni/(?P<participant_id>[0-9]+)/turnusy/(?P<batch_id>[0-9]+)/usun/$', views.batch_participant_delete,
        name='batch_participant_delete'),
    url(r'^podopieczni/(?P<pk>[0-9]+)/edycja/$', views.edit_participant, name='edit_participant'),
    url(r'^podopieczni/usun/(?P<pk>[0-9]+)/$', views.delete_participant, name='delete_participant'),
    url(r'^rezerwacje/dodaj/$', views.add_booking, name='add_booking'),
    url(r'^rezerwacje/dodaj-1/(?P<pk>[0-9]+)/$', views.add_booking3, name='add_booking3'),
    url(r'^rezerwacje/dodaj-2/(?P<pk>[0-9]+)/$', views.add_booking_2, name='add_booking_2'),
    url(r'^rezerwacje/dodaj-z-posilkami/$', views.add_meals_booking, name='add_meals_booking'),
    url(r'^rezerwacje/(?P<pk>[0-9]+)/edycja-z-posilkami/$', views.edit_meals_booking, name='edit_meals_booking'),
    url(r'^rezerwacje/(?P<pk>[0-9]+)/edycja/$', views.edit_booking, name='edit_booking'),
    url(r'^rezerwacje/(?P<pk>[0-9]+)/edycja-2/$', views.edit_booking_2, name='edit_booking_2'),
    url(r'^rezerwacje/usun/(?P<pk>[0-9]+)/$', views.delete_booking, name='delete_booking'),
    url(r'^rezerwacje/usun/(?P<pk>[0-9]+)/$', views.delete_meals_booking, name='delete_meals_booking'),
    url(r'^rezerwacje-pokojow/$', views.all_bookings, name='all_bookings'),
    url(r'^pobyty-z-posilkami/$', views.all_bookings_meals, name='all_bookings_meals'),
    url(r'^rezerwacje/platnosci/(?P<booking_id>[0-9]+)/$', views.booking_payment, name='booking_payment'),
    url(r'^rezerwacje/(?P<pk>[0-9]+)/$', views.booking_details, name='booking_details'),
    url(r'^podopieczni/csv/$', views.get_participants_from_csv, name='get_participants_from_csv'),
    url(r'^podopieczni/aktualizacja/$', views.update_participants_count, name='update_participants_count')
]
