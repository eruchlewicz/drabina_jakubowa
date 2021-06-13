from django.contrib import admin
from .models import *
from django.utils.html import linebreaks
from django.conf.locale.en import formats as en_formats

en_formats.DATETIME_FORMAT = "d.m.Y H:i"


class BatchVolunteerAdmin(admin.ModelAdmin):
    ordering = ('-batch__begin_date', 'batch__name', 'batch__institution__city')
    list_filter = ('batch', 'batch__institution__city', 'batch__begin_date', 'checked')
    list_display = ('batch', 'volunteer', 'unique_key', 'was_there', 'checked')
    search_fields = ['volunteer__surname', 'volunteer__first_name', 'unique_key', 'batch__begin_date', 'batch__name',
                     'batch__institution__city']


class BatchParticipantAdmin(admin.ModelAdmin):
    ordering = ('-batch__begin_date', 'batch__name', 'batch__institution__city')
    list_filter = ('batch', 'batch__institution__city', 'batch__begin_date')
    list_display = ('batch', 'participant', 'unique_key', 'is_part_paid', 'is_paid', 'payment_id')
    search_fields = ['participant__surname', 'participant__first_name', 'batch__begin_date', 'payment_id', 
                     'unique_key', 'batch__name', 'batch__institution__city']


class BatchAdmin(admin.ModelAdmin):
    def get_institution(self, obj):
        return linebreaks(obj.institution)
    get_institution.short_description = u'Placówka'
    get_institution.admin_ordering_field = 'institution'
    get_institution.allow_tags = True

    def get_nurses(self, obj):
        return "\n".join([e.first_name+" "+e.surname for e in obj.nurse.all()])
    get_nurses.short_description = u'Pielęgniarki'

    def get_doctors(self, obj):
        return "\n".join([e.first_name+" "+e.surname for e in obj.doctor.all()])
    get_doctors.short_description = u'Lekarze'
    ordering = ('-begin_date', 'name',)
    list_filter = ('name', 'institution__city', 'begin_date')
    list_display = ('name', 'begin_date', 'end_date', 'is_closed', 'get_institution', 'main_coordinator', 
                    'auxiliary_coordinator', 'main_priest', 'auxiliary_priest', 'get_nurses', 'get_doctors')
    search_fields = ['begin_date', 'name']


class CoordinatorAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('volunteer', 'user',)


class DoctorAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('volunteer', 'user')


class NurseAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('volunteer', 'user')


class InstitutionAdmin(admin.ModelAdmin):
    def get_institution(self, obj):
        return linebreaks(obj.name)
    get_institution.short_description = u'Placówka'
    get_institution.admin_ordering_field = 'institution'
    get_institution.allow_tags = True
    ordering = ('name',)
    list_display = ('get_institution', 'address', 'zip_code', 'city', 'director')


class ParticipantAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('surname', 'first_name', 'pesel', 'phone_number', 'guardian_phone_number', 'flower',
                    'others')
    list_filter = ('flower',)
    search_fields = ['surname', 'first_name']


class PriestAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('first_name', 'surname')


class DirectorAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('first_name', 'surname', 'phone_number', 'email_address')


class PersonAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('first_name', 'surname', 'pesel', 'address', 'zip_code', 'city', 'phone_number', 'email_address')


class RetreatOrMusicTrainingAdmin(admin.ModelAdmin):
    def get_institution(self, obj):
        return linebreaks(obj.institution)
    get_institution.short_description = u'Placówka'
    get_institution.admin_ordering_field = 'institution'
    get_institution.allow_tags = True
    ordering = ('-begin_date', 'name',)
    list_filter = ('type', 'institution__city', 'begin_date', 'with_accommodation')
    list_display = ('name', 'begin_date', 'end_date', 'is_closed', 'get_institution', 'main_coordinator',
                    'auxiliary_coordinator', 'with_accommodation')
    search_fields = ['begin_date', 'end_date', 'name']


class RetreatOrMusicTrainingPersonAdmin(admin.ModelAdmin):
    ordering = ('-retreat_or_music_training__begin_date', 'retreat_or_music_training__name',
                'retreat_or_music_training__institution__city')
    list_filter = ('retreat_or_music_training__name', 'retreat_or_music_training__institution__city', 'retreat_or_music_training__begin_date')
    list_display = ('retreat_or_music_training', 'person', 'accommodation', 'saturday_sunday', 'is_paid', 'payment_id')
    search_fields = ['person__surname', 'person__first_name', 'retreat_or_music_training__begin_date']


class VolunteerAdmin(admin.ModelAdmin):
    ordering = ('surname', 'first_name',)
    list_display = ('surname', 'first_name', 'pesel', 'city', 'phone_number', 'email_address', 'user')
    list_filter = ('city',)
    search_fields = ['surname', 'first_name', 'user__username']


class EventAdmin(admin.ModelAdmin):
    def get_nurses(self, obj):
        return "\n".join([e.first_name+" "+e.surname for e in obj.nurse.all()])
    get_nurses.short_description = u'Pielęgniarki'

    def get_doctors(self, obj):
        return "\n".join([e.first_name+" "+e.surname for e in obj.doctor.all()])
    get_doctors.short_description = u'Lekarze'
    ordering = ('-begin_date', 'name',)
    list_filter = ('begin_date',)
    list_display = ('name', 'begin_date', 'end_date', 'is_closed', 'main_coordinator', 'auxiliary_coordinator', 
                    'get_nurses', 'get_doctors', 'info', 'price')
    search_fields = ['begin_date', 'end_date']


class EventParticipantAdmin(admin.ModelAdmin):
    def get_flower(self, obj):
        return obj.participant.get_flower_display()

    def get_others(self, obj):
        return obj.participant.others
    get_flower.short_description = 'Kwiatek'
    get_flower.admin_order_field = 'participant__flower'
    get_others.short_description = 'Inne'
    get_others.admin_order_field = 'participant__others'
    ordering = ('-event__begin_date', 'event__name')
    list_filter = ('event__name', 'event__begin_date', 'participant__flower')
    list_display = ('event', 'participant', 'get_flower', 'get_others', 'is_paid', 'payment_id')
    search_fields = ['participant__surname', 'participant__first_name', 'event__begin_date', 'payment_id']


class EventVolunteerAdmin(admin.ModelAdmin):
    def get_phone_number(self, obj):
        return obj.volunteer.phone_number
    get_phone_number.short_description = 'Numer telefonu'
    get_phone_number.admin_order_field = 'volunteer__phone_number'

    def get_city(self, obj):
        return obj.volunteer.city
    get_city.short_description = 'Miasto'
    get_city.admin_order_field = 'volunteer__city'
    ordering = ('-event__begin_date', 'event__name')
    list_filter = ('event__name', 'event__begin_date', 'volunteer__city')
    list_display = ('event', 'volunteer', 'get_city', 'get_phone_number', 'is_paid', 'payment_id')
    search_fields = ['volunteer__surname', 'volunteer__first_name', 'event__begin_date']


class EventPostAdmin(admin.ModelAdmin):
    ordering = ('-begin_date',)
    list_display = ('title', 'content', 'batch', 'event', 'retreat_or_music_training', 'begin_date')


admin.site.register(Director, DirectorAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Priest, PriestAdmin)
admin.site.register(Coordinator, CoordinatorAdmin)
admin.site.register(Nurse, NurseAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(BatchParticipant, BatchParticipantAdmin)
admin.site.register(BatchVolunteer, BatchVolunteerAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventVolunteer, EventVolunteerAdmin)
admin.site.register(EventParticipant, EventParticipantAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(RetreatOrMusicTraining, RetreatOrMusicTrainingAdmin)
admin.site.register(RetreatOrMusicTrainingPerson, RetreatOrMusicTrainingPersonAdmin)
admin.site.register(EventPost, EventPostAdmin)
