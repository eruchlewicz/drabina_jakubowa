from django.conf.urls import url
from . import views
from .views import *
from django.contrib.auth.decorators import login_required

app_name = 'coordinatepanel'
urlpatterns = [
    url(r'^logowanie/$', views.coordinator_login, name='coordinator_login'),
    url(r'^wylogowanie/$', views.logout_view, name='logout'),
    url(r'^kalendarz/$', views.calendar, name='calendar'),
    url(r'^warsztaty-i-rekolekcje/$', views.music_trainings, name='music_trainings'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/$', views.training_details, name='training_details'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/raport.pdf/$', login_required(TrainingReportPDFView.as_view()),
        name='training_report'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/$', views.training_people, name='training_people'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/(?P<person_id>[0-9]+)/$', views.person_details,
        name='person_details'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/(?P<training_person_id>[0-9]+)/usun/$', views.delete_person,
        name='delete_person'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/(?P<training_person_id>[0-9]+)/edytuj/$',
        views.training_person_edit, name='training_person_edit'),
    url(r'^warsztaty-i-rekolekcje/(?P<pk>[0-9]+)/uczestnicy/(?P<training_person_id>[0-9]+)/platnosci/$',
        views.person_payment, name='person_payment'),
    url(r'^statystyki/$', views.statistics, name='statistics'),
    url(r'^turnus/(?P<pk>[0-9]+)/$', views.batch_view, name='batch_view'),
    url(r'^turnus/(?P<pk>[0-9]+)/karta-obiegowa.pdf/$', login_required(CirculationCardPDFView.as_view()),
        name='circulation_card'),
    url(r'^turnus/(?P<pk>[0-9]+)/raport-pokoje.pdf/$', login_required(RoomsReportPDFView.as_view()),
        name='rooms_report'),
    url(r'^turnus/(?P<pk>[0-9]+)/pusty-raport-pokoje.pdf/$', login_required(RoomsEmptyReportPDFView.as_view()),
        name='empty_rooms_report'),
    url(r'^turnus/(?P<pk>[0-9]+)/wolontariusze/$', views.volunteers, name='volunteers_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/wolontariusze/(?P<volunteer_id>[0-9]+)/wpisz/$', views.move_volunteer_to_base_list,
        name='move_volunteer_to_base_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/wolontariusze/(?P<volunteer_id>[0-9]+)/rezerwowa/$',
        views.move_volunteer_to_reserve_list, name='move_volunteer_to_reserve_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/wolontariusze/raport-wolontariusze.pdf/$',
        login_required(VolunteersReportPDFView.as_view()), name='volunteers_report'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/$', views.participants, name='participants_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<participant_id>[0-9]+)/wpisz/$', views.move_participant_to_base_list,
        name='move_participant_to_base_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<participant_id>[0-9]+)/rezerwowa/$',
        views.move_participant_to_reserve_list, name='move_participant_to_reserve_list'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<batch_participant_id>[0-9]+)/platnosci/$', views.participant_payment,
        name='participant_payment'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/raport-podopieczni.pdf/$',
        login_required(ParticipantsReportPDFView.as_view()), name='participants_report'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<participant_id>[0-9]+)/$', views.participant_details,
        name='participant_details'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<participant_id>[0-9]+)/zdjecie/$', views.participant_photo_edit,
        name='participant_photo_edit'),
    url(r'^turnus/(?P<pk>[0-9]+)/wolontariusze/(?P<volunteer_id>[0-9]+)/$', views.volunteer_details,
        name='volunteer_details'),
    url(r'^turnus/(?P<pk>[0-9]+)/wolontariusze/(?P<batch_volunteer_id>[0-9]+)/edytuj/$', views.batch_volunteer_edit,
        name='batch_volunteer_edit'),
    url(r'^turnus/(?P<pk>[0-9]+)/podopieczni/(?P<batch_participant_id>[0-9]+)/edytuj/$', views.batch_participant_edit,
        name='batch_participant_edit'),
    url(r'^turnusy/$', views.batches, name='batches'),
    url(r'^turnus/(?P<batch_id>[0-9]+)/podopieczni/(?P<batch_participant_id>[0-9]+)/usun/$', views.delete_participant,
        name='delete_participant'),
    url(r'^turnus/(?P<batch_id>[0-9]+)/wolontariusze/(?P<batch_volunteer_id>[0-9]+)/usun/$', views.delete_volunteer,
        name='delete_volunteer'),
    url(r'^turnus/(?P<pk>[0-9]+)/(?P<id>[\w{}.-]{1,36})/zaswiadczenie.pdf/$',
        login_required(CertificatePDFView.as_view()), name='certificate'),
    url(r'^turnusy/wolontariusze/(?P<pk>[\w{}.-]{1,36})/umowa.pdf/$',
        login_required(VolunteerContractPDFView.as_view()), name='contract'),
    url(r'^turnusy/wolontariusze/(?P<pk>[0-9]+)/umowy.pdf/$',
        login_required(AllVolunteersContractPDFView.as_view()), name='contracts'),
    url(r'^turnusy/(?P<pk>[\w{}.-]{1,36})/umowa.pdf/$',
        login_required(ContractPDFView.as_view()), name='coordinator_contract'),
    url(r'^wydarzenia/$', views.events_view, name='events'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/$', views.event_details, name='event_details'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/informacje/$', views.event_info_edit, name='event_info_edit'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/wolontariusze/$', views.event_volunteers, name='event_volunteers'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/wolontariusze/(?P<event_volunteer_id>[0-9]+)/platnosci/$',
        views.event_volunteer_payment, name='event_volunteer_payment'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/podopieczni/$', views.event_participants, name='event_participants'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/podopieczni/(?P<event_participant_id>[0-9]+)/edycja/$',
        views.event_participant_edit, name='event_participant_edit'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/podopieczni/(?P<event_participant_id>[0-9]+)/platnosci/$',
        views.event_participant_payment, name='event_participant_payment'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/podopieczni/(?P<participant_id>[0-9]+)/$', views.event_participant_details,
        name='event_participant_details'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/wolontariusze/(?P<volunteer_id>[0-9]+)/$', views.event_volunteer_details,
        name='event_volunteer_details'),
    url(r'^wydarzenia/(?P<event_id>[0-9]+)/podopieczni/(?P<event_participant_id>[0-9]+)/usun/$',
        views.delete_event_participant, name='delete_event_participant'),
    url(r'^wydarzenia/(?P<event_id>[0-9]+)/wolontariusze/(?P<event_volunteer_id>[0-9]+)/usun/$',
        views.delete_event_volunteer, name='delete_event_volunteer'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/raport-wydarzenie.pdf/$', login_required(EventReportPDFView.as_view()),
        name='event_report'),
    url(r'^wydarzenia/(?P<pk>[0-9]+)/lista-wydarzenie.pdf/$', login_required(EventReportListPDFView.as_view()),
        name='event_report_list'),
    url(r'^pliki/$', views.get_files, name='get_files'),
    url(r'^statystyki/aktualizacja/$', views.update_participants_count, name='update_participants_count')
]
