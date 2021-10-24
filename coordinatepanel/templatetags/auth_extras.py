from django import template
from django.contrib.auth.models import Group
from coordinatepanel.models import *
from dj.models import *
from datetime import datetime


register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='key_fit')
def key_fit(key):
    batch_volunteer = BatchVolunteer.objects.filter(unique_key=key)
    return batch_volunteer


@register.filter(name='get_age')
def get_age(pesel):
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
        age = abs(datetime.now() - birthday).days / 365.25
        age = int(age)
    else:
        age = 'err'
    return age


@register.filter(name='has_birthday')
def has_birthday(event_person):
    if type(event_person) in [BatchVolunteer, BatchParticipant]:
        begin_date = event_person.batch.begin_date
        end_date = event_person.batch.end_date
    elif type(event_person) in [EventVolunteer, EventParticipant]:
        begin_date = event_person.event.begin_date
        end_date = event_person.event.end_date
    else:
        begin_date = event_person.retreat_or_music_training.begin_date
        end_date = event_person.retreat_or_music_training.end_date

    if type(event_person) in [BatchVolunteer, EventVolunteer]:
        pesel = event_person.volunteer.pesel
    elif type(event_person) in [BatchParticipant, EventParticipant]:
        pesel = event_person.participant.pesel
    else:
        pesel = event_person.person.pesel

    mm = pesel[2:4]
    dd = pesel[4:6]
    if int(mm) > 12:
        mm = int(mm) - 20

    if 0 < int(mm) <= 12 and 0 < int(dd) <= 31:
        birthday_begin_year = datetime.strptime(str(begin_date.year) + " " + str(mm) + " " + str(dd), '%Y %m %d')
        birthday_end_year = datetime.strptime(str(end_date.year) + " " + str(mm) + " " + str(dd), '%Y %m %d')
        return (
            begin_date.date() <= birthday_begin_year.date() <= end_date.date() or
            begin_date.date() <= birthday_end_year.date() <= end_date.date()
        )
    else:
        return False


@register.filter(name='which_batch')
def which_batch(event_person):
    end_date = event_person.batch.end_date

    if type(event_person) == BatchVolunteer:
        event_count = BatchVolunteer.objects.filter(
            volunteer__id=event_person.volunteer.id, batch__begin_date__lte=end_date
        ).count()
    else:
        event_count = BatchParticipant.objects.filter(
            participant__id=event_person.participant.id, batch__begin_date__lte=end_date
        ).count()

    return event_count


@register.filter(name='is_nurse')
def is_nurse(batch, volunteer):
    return batch.nurse.filter(volunteer_id=volunteer.id).exists()


@register.filter(name='is_doctor')
def is_doctor(batch, volunteer):
    return batch.doctor.filter(volunteer_id=volunteer.id).exists()


@register.filter(name='volunteer_participant')
def volunteer_participant(batch, volunteer):
    return BatchParticipant.objects.filter(batch=batch, volunteer=volunteer)


@register.filter(name='empty_rooms_volunteer')
def empty_rooms_volunteer(batch, batch_volunteer):
    rooms = Room.objects.all()
    begin_date = batch.begin_date
    end_date = batch.end_date
    bookings = Booking.objects.exclude(room=None).filter(begin_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=begin_date, end_date__lte=end_date) | \
               Booking.objects.exclude(room=None).filter(end_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=end_date, begin_date__lte=begin_date)
    retreats = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__begin_date__lte=end_date,
                                                           retreat_or_music_training__begin_date__gte=begin_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__gte=begin_date,
                                                           retreat_or_music_training__end_date__lte=end_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__lte=end_date,
                                                           retreat_or_music_training__begin_date__gte=begin_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__gte=end_date,
                                                           retreat_or_music_training__begin_date__lte=begin_date)
    if batch.institution.city == "Brańszczyk":
        participants = BatchParticipant.objects.filter(batch=batch)
        volunteers = BatchVolunteer.objects.filter(batch=batch)

        for booking in bookings:
            for room in rooms:
                for r in booking.room.all():
                    if r == room:
                        rooms = rooms.exclude(number=room.number)

        for retreat in retreats:
            for room in rooms:
                if retreat.room == room:
                    rooms = rooms.exclude(number=room.number)

        for room in rooms:
            count = 0
            for participant in participants:
                if participant.room == room:
                    rooms = rooms.exclude(number=room.number)
                    break
            for volunteer in volunteers:
                if volunteer.room == room:
                    count += 1
                    if not volunteer == batch_volunteer:
                        if room.beds_number <= count:
                            rooms = rooms.exclude(number=room.number)
                            break
                        elif not volunteer.room_sex == batch_volunteer.volunteer.sex:
                            rooms = rooms.exclude(number=room.number)
                            break
                    else:
                        break

        return rooms
    else:
        return Room.objects.none()


@register.filter(name='empty_rooms_participant')
def empty_rooms_participant(batch, batch_participant):
    rooms = Room.objects.all()
    begin_date = batch.begin_date
    end_date = batch.end_date
    home = Home.objects.first()
    city = home.city
    bookings = Booking.objects.exclude(room=None).filter(begin_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=begin_date, end_date__lte=end_date) | \
               Booking.objects.exclude(room=None).filter(end_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=end_date, begin_date__lte=begin_date)
    retreats = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__begin_date__lte=end_date,
                                                           retreat_or_music_training__begin_date__gte=begin_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__gte=begin_date,
                                                           retreat_or_music_training__end_date__lte=end_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__lte=end_date,
                                                           retreat_or_music_training__begin_date__gte=begin_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__gte=end_date,
                                                           retreat_or_music_training__begin_date__lte=begin_date)
    if batch.institution.city == city:
        participants = BatchParticipant.objects.filter(batch=batch)
        volunteers = BatchVolunteer.objects.filter(batch=batch)

        for booking in bookings:
            for room in rooms:
                for r in booking.room.all():
                    if r == room:
                        rooms = rooms.exclude(number=room.number)

        for retreat in retreats:
            for room in rooms:
                if retreat.room == room:
                    rooms = rooms.exclude(number=room.number)

        for room in rooms:
            count = 0
            for volunteer in volunteers:
                if volunteer.room == room:
                    rooms = rooms.exclude(number=room.number)
                    break
            for participant in participants:
                if participant.room == room:
                    count += 1
                    if not participant == batch_participant:
                        if room.beds_number <= count:
                            rooms = rooms.exclude(number=room.number)
                            break
                        elif not participant.room_sex == batch_participant.participant.sex:
                            rooms = rooms.exclude(number=room.number)
                            break
                    else:
                        break
        return rooms
    else:
        return Room.objects.none()


@register.filter(name='empty_rooms_participant')
def empty_rooms_person(retreat, retreat_person):
    rooms = Room.objects.all()
    begin_date = retreat.begin_date
    end_date = retreat.end_date
    home = Home.objects.first()
    city = home.city
    bookings = Booking.objects.exclude(room=None).filter(begin_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=begin_date, end_date__lte=end_date) | \
               Booking.objects.exclude(room=None).filter(end_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=end_date, begin_date__lte=begin_date)
    participants = BatchParticipant.objects.filter(batch__institution__city=city, batch__begin_date__lte=end_date,
                                                   batch__begin_date__gte=begin_date) | \
                BatchParticipant.objects.filter(batch__institution__city=city, batch__end_date__gte=begin_date,
                                                batch__end_date__lte=end_date) | \
                BatchParticipant.objects.filter(batch__institution__city=city, batch__end_date__lte=end_date,
                                                batch__begin_date__gte=begin_date) | \
                   BatchParticipant.objects.filter(batch__institution__city=city, batch__end_date__gte=end_date,
                                                   batch__begin_date__lte=begin_date)
    volunteers = BatchVolunteer.objects.filter(batch__institution__city=city, batch__begin_date__lte=end_date,
                                               batch__begin_date__gte=begin_date) | \
                BatchVolunteer.objects.filter(batch__institution__city=city, batch__end_date__gte=begin_date,
                                              batch__end_date__lte=end_date) | \
                BatchVolunteer.objects.filter(batch__institution__city=city, batch__end_date__lte=end_date,
                                              batch__begin_date__gte=begin_date) | \
                 BatchVolunteer.objects.filter(batch__institution__city=city, batch__end_date__gte=end_date,
                                               batch__begin_date__lte=begin_date)
    retreat_people = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training=retreat)

    for booking in bookings:
        for room in rooms:
            for r in booking.room.all():
                if r == room:
                    rooms = rooms.exclude(number=room.number)

    for room in rooms:
        count = 0
        for volunteer in volunteers:
            if volunteer.room == room:
                rooms = rooms.exclude(number=room.number)
                break
        for participant in participants:
            if participant.room == room:
                rooms = rooms.exclude(number=room.number)
                break
        for person in retreat_people:
            if person.room == room:
                count += 1
                if not person == retreat_person:
                    if room.beds_number <= count:
                        rooms = rooms.exclude(number=room.number)
                        break
                    elif not person.room_sex == retreat_person.person.sex:
                        rooms = rooms.exclude(number=room.number)
                        break
                else:
                    break

    return rooms


@register.filter(name='empty_rooms')
def empty_rooms(begin_date, end_date, booking_id):
    rooms = Room.objects.all()
    bookings = Booking.objects.exclude(room=None).filter(begin_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=begin_date, end_date__lte=end_date) | \
               Booking.objects.exclude(room=None).filter(end_date__lte=end_date, begin_date__gte=begin_date) | \
               Booking.objects.exclude(room=None).filter(end_date__gte=end_date, begin_date__lte=begin_date)
    home = Home.objects.first()
    city = home.city
    batches = Batch.objects.filter(institution__city=city, begin_date__lte=end_date, begin_date__gte=begin_date) | \
              Batch.objects.filter(institution__city=city, end_date__gte=begin_date, end_date__lte=end_date) | \
              Batch.objects.filter(institution__city=city, end_date__lte=end_date, begin_date__gte=begin_date) | \
              Batch.objects.filter(institution__city=city, end_date__gte=end_date, begin_date__lte=begin_date)
    retreats = RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__begin_date__lte=end_date,
                                                           retreat_or_music_training__begin_date__gte=begin_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__gte=begin_date,
                                                           retreat_or_music_training__end_date__lte=end_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__lte=end_date,
                                                           retreat_or_music_training__begin_date__gte=begin_date) | \
               RetreatOrMusicTrainingPerson.objects.filter(retreat_or_music_training__end_date__gte=end_date,
                                                           retreat_or_music_training__begin_date__lte=begin_date)

    for batch in batches:
        participants = BatchParticipant.objects.filter(batch=batch)
        volunteers = BatchVolunteer.objects.filter(batch=batch)
        for room in rooms:
            for participant in participants:
                if participant.room == room:
                    rooms = rooms.exclude(number=room.number)
                    break
            for volunteer in volunteers:
                if volunteer.room == room:
                    rooms = rooms.exclude(number=room.number)
                    break

    for booking in bookings:
        if not booking.id == booking_id:
            for room in rooms:
                for r in booking.room.all():
                    if r == room:
                        rooms = rooms.exclude(number=room.number)

    for retreat in retreats:
        for room in rooms:
            if retreat.room == room:
                rooms = rooms.exclude(number=room.number)

    return rooms
