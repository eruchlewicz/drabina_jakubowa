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


class HomeTests(TestCase):
    def test_home_str(self):
        home = Home.objects.create(
            name='Dom',
            address='Testowa 1',
            zip_code='00-000',
            city='Test',
            phone_number='777777777',
            nip="12345678910",
            regon=12345678,
            page_url="test.com",
            email_address="test@test.com"
        )
        self.assertEqual(str(home), home.name+" "+home.city)

    def test_home_delete(self):
        home = Home.objects.create(
            name='Dom',
            address='Testowa 1',
            zip_code='00-000',
            city='Test',
            phone_number='777777777',
            nip="12345678910",
            regon=12345678,
            page_url="test.com",
            email_address="test@test.com"
        )
        result = home.delete()
        self.assertIs(result, None)

    def test_home_load(self):
        home = Home.objects.create(
            name='Dom',
            address='Testowa 1',
            zip_code='00-000',
            city='Test',
            phone_number='777777777',
            nip="12345678910",
            regon=12345678,
            page_url="test.com",
            email_address="test@test.com"
        )
        result = home.load()
        self.assertIs(result.id, 1)
        home2 = Home.objects.create(
            name='Dom2',
            address='Testowa 2',
            zip_code='00-000',
            city='Test2',
            phone_number='777777777',
            nip="12345678910",
            regon=12345678,
            page_url="test2.com",
            email_address="test2@test.com"
        )
        result2 = home2.load()
        self.assertIs(result2.id, 1)


class CongregationTests(TestCase):
    def test_congregation_str(self):
        congregation = Congregation.objects.create(
            congregation='Zgromadzenie Orionistów',
            chief='ks. Jan Kowalski',
            community='Drabina Jakubowa',
            director='ks. Paweł Nowak',
            main_institution='ul. Testowa 1, 00-000 Testowo'
        )
        self.assertEqual(str(congregation), congregation.congregation)

    def test_congregation_delete(self):
        congregation = Congregation.objects.create(
            congregation='Zgromadzenie Orionistów',
            chief='ks. Jan Kowalski',
            community='Drabina Jakubowa',
            director='ks. Paweł Nowak',
            main_institution='ul. Testowa 1, 00-000 Testowo'
        )
        result = congregation.delete()
        self.assertIs(result, None)

    def test_congregation_load(self):
        congregation = Congregation.objects.create(
            congregation='Zgromadzenie Orionistów',
            chief='ks. Jan Kowalski',
            community='Drabina Jakubowa',
            director='ks. Paweł Nowak',
            main_institution='ul. Testowa 1, 00-000 Testowo'
        )
        result = congregation.load()
        self.assertIs(result.id, 1)
        congregation2 = Congregation.objects.create(
            congregation='Zgromadzenie Orionistów',
            chief='ks. Jan Kowalski',
            community='Drabina Jakubowa',
            director='ks. Paweł Nowak',
            main_institution='ul. Testowa 1, 00-000 Testowo'
        )
        result2 = congregation2.load()
        self.assertIs(result2.id, 1)


class RoomTests(TestCase):
    def test_room_str(self):
        room = Room.objects.create(
            number='1',
            beds_number='5',
            floor_number=0,
            has_bathroom=True
        )
        self.assertEqual(str(room), room.number)


class PostTests(TestCase):
    def test_post_str(self):
        post = Post.objects.create(
            title='Test',
            content='Testowanie',
            date=today
        )
        self.assertIs(str(post), post.title)


class PriceTests(TestCase):
    def test_price_str(self):
        price = Price.objects.create(
            service='Testowanie',
            price='100.00',
        )
        self.assertEqual(str(price), price.service)


class BookingTests(TestCase):
    def test_booking_str(self):
        booking = Booking.objects.create(
            first_name='Jan',
            surname='Kowalski',
            phone_number='555555555',
            email_address='test@test.com',
            begin_date=today,
            end_date=today
        )
        self.assertEqual(str(booking), booking.first_name+" "+booking.surname)


