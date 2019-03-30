from datetime import timedelta
from django.db.models import Sum
from django.test import Client
from django.test import RequestFactory
from django.test import TestCase
from django.utils import timezone
from .forms import *
from .models import *
from django.core.urlresolvers import reverse

client = Client()
today = timezone.now()


class DirectorTests(TestCase):
    def test_director_str(self):
        director = Director.objects.create(
            first_name='Jan',
            surname='Kowalski',
            phone_number='555555555',
            email_address='test@test.com'
        )
        self.assertEqual(str(director), director.first_name+" "+director.surname)


class InstitutionTests(TestCase):
    def test_director_str(self):
        director = Director.objects.create(
            first_name='Jan',
            surname='Kowalski',
            phone_number='555555555',
            email_address='test@test.com'
        )
        institution = Institution.objects.create(
            name='Dom rekolekcyjny',
            director=director,
            city='Brańszczyk',
            zip_code='00-000',
            address='Jana Pawła II 1'
        )
        self.assertEqual(str(institution), institution.name+" "+institution.city)


class VolunteerTests(TestCase):
    def test_volunteer_str(self):
        volunteer = Volunteer.objects.create(
            first_name='Jan',
            surname='Kowalski',
            pesel='12345678910',
            sex='M',
            age='D',
            phone_number='555555555',
            email_address='test@test.com',
            city='Testowo',
            zip_code='00-000',
            address='Testowa 1',
            education='W',
            how_know_dj='Z',
            drugs='N',
            guardian_phone_number='123456789'
        )
        self.assertEqual(str(volunteer), volunteer.first_name+" "+volunteer.surname)


class PriestTests(TestCase):
    def test_priest_str(self):
        priest = Priest.objects.create(
            first_name='Jan',
            surname='Kowalski',
            pesel='12345678910',
            phone_number='555555555',
            email_address='test@test.com',
            city='Testowo',
            zip_code='00-000',
            address='Testowa 1'
        )
        self.assertEqual(str(priest), "ks. "+priest.first_name+" "+priest.surname)


class CoordinatorTests(TestCase):
    def test_coordinator_str(self):
        coordinator = Coordinator.objects.create(
            first_name='Jan',
            surname='Kowalski',
            pesel='12345678910',
            phone_number='555555555',
            email_address='test@test.com',
            city='Testowo',
            zip_code='00-000',
            address='Testowa 1'
        )
        self.assertEqual(str(coordinator), coordinator.first_name+" "+coordinator.surname)


class NurseTests(TestCase):
    def test_nurse_str(self):
        nurse = Nurse.objects.create(
            first_name='Jan',
            surname='Kowalski',
        )
        self.assertEqual(str(nurse), nurse.first_name+" "+nurse.surname)
