from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from coordinatepanel.models import Batch, Institution, Director, Coordinator, Volunteer, BatchVolunteer
from django.contrib.auth.models import User, Group
import logging
from django.utils import timezone
from datetime import timedelta
now = timezone.now()


class DJLoginRegister(StaticLiveServerTestCase):

    def setUp(self):
        selenium_logger = logging.getLogger(
            'selenium.webdriver.remote.remote_connection')
        selenium_logger.setLevel(logging.WARN)
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1200, 600)
        director = Director.objects.create(first_name="Jan", surname="Kowalski", phone_number="777777777",
                                           email_address="jk@gmail.com")
        institution = Institution.objects.create(name="Dom rekolekcyjny", director=director, city="Białystok",
                                                 zip_code="15-860", address="Radzymińska 1")
        batch = Batch.objects.create(name="Test", institution=institution, begin_date=now+timedelta(1),
                                     end_date=now+timedelta(2))
        user_coo = User.objects.create(username="coordinator", password="testowe123", email="test@test.com")
        user_vol = User.objects.create(username="volunteer", password="testowe123", email="test@test.com")
        Coordinator.objects.create(user=user_coo, first_name="Test", surname="Testowy", phone_number="123456789",
                                   email_address="test@test.com", city="Białystok", zip_code="15-563",
                                   address="Liściasta 25")
        volunteer = Volunteer.objects.create(user=user_vol, first_name="Test", surname="Testowy", phone_number="123456789",
                                             email_address="test@test.com", city="Białystok", zip_code="15-563",
                                             address="Liściasta 24", age='D', education='W', physical_health=True,
                                             is_first_time=False, mental_health=True, drugs='N', how_know_dj='Z',
                                             data_processing_agreement=True, photographing_agreement=True)

        Group.objects.get_or_create(name='Wolontariusze')
        group = Group.objects.get(name="Wolontariusze")
        group_id = group.id
        user_vol.groups.add(group_id)

        Group.objects.get_or_create(name='Koordynatorzy')
        group2 = Group.objects.get(name="Koordynatorzy")
        group_id2 = group2.id
        user_coo.groups.add(group_id2)

        BatchVolunteer.objects.create(volunteer=volunteer, batch=batch)

    def test_open_homepage(self):
        driver = self.driver
        driver.get(self.live_server_url)
        self.assertIn("Drabina Jakubowa", driver.title)
        self.assertTrue(driver.current_url == self.live_server_url + '/')

    def test_account(self):
        driver = self.driver
        wait = WebDriverWait(driver, 20)
        driver.get(self.live_server_url + '/logowanie/')
        user = User.objects.filter(username="volunteer").first()
        password = 'qqqqqqqq'
        user.set_password(password)
        user.save()

        if user is not None:
            driver.find_element_by_id('id_username').send_keys(user.username)
            driver.find_element_by_id('id_password').send_keys(password)
            button = wait.until(EC.element_to_be_clickable((By.ID, 'login_btn')))
            button.click()

        wait.until(EC.presence_of_element_located((By.ID, 'batches')))
        self.assertTrue(driver.current_url == self.live_server_url + '/turnusy/')

        driver.find_element_by_link_text('Konto').click()

        wait.until(EC.presence_of_element_located((By.ID, 'account_edit_link')))
        self.assertTrue(driver.current_url == self.live_server_url + '/dane/')

        driver.find_element_by_id("change_password_link").click()
        self.assertTrue(driver.current_url == self.live_server_url + '/dane/haslo/')

        password2 = 'AlaMaKot12'

        driver.find_element_by_id("id_old_password").send_keys(password)
        driver.find_element_by_id("id_new_password1").send_keys(password2)
        driver.find_element_by_id("id_new_password2").send_keys(password2)
        driver.find_element_by_id("change_password_btn").click()

        wait.until(EC.presence_of_element_located((By.ID, 'account_edit_link')))
        self.assertTrue(driver.current_url == self.live_server_url + '/dane/')

    def test_register_from_homepage_link(self):
        driver = self.driver
        driver.get(self.live_server_url)
        wait = WebDriverWait(driver, 10)
        register_link = wait.until(EC.presence_of_element_located((By.ID, 'register_link')))
        register_link.click()
        self.assertTrue(driver.current_url == self.live_server_url + '/rejestracja/')

        driver.find_element_by_id('id_username').send_keys("ewelina")
        driver.find_element_by_id('id_email').send_keys("ewelina@gmail.com")
        driver.find_element_by_id('id_password').send_keys("eeeeeeee")
        driver.find_element_by_id('id_password_confirmation').send_keys("eeeeeeee")
        driver.find_element_by_id('id_first_name').send_keys("Ewelina")
        driver.find_element_by_id('id_last_name').send_keys("Ruchlewicz")
        Select(driver.find_element_by_id('id_batch')).select_by_index(1)
        Select(driver.find_element_by_id('id_sex')).select_by_index(1)
        driver.find_element_by_id('id_pesel').send_keys("96031900000")
        Select(driver.find_element_by_id('id_age')).select_by_value('D')
        driver.find_element_by_id('id_phone_number').send_keys("972039014")
        driver.find_element_by_id('id_city').send_keys("Białystok")
        driver.find_element_by_id('id_zip_code').send_keys("15-563")
        driver.find_element_by_id('id_address').send_keys("Liściasta 24")
        Select(driver.find_element_by_id('id_education')).select_by_value('S')
        Select(driver.find_element_by_id('id_how_know_dj')).select_by_value('Z')
        driver.find_element_by_id('id_physical_health').click()
        driver.find_element_by_id('id_mental_health').click()
        Select(driver.find_element_by_id('id_drugs')).select_by_value('N')
        driver.find_element_by_id('id_guardian_phone_number').send_keys("888777666")
        driver.find_element_by_id('id_data_processing_agreement').click()
        driver.find_element_by_id('id_photographing_agreement').click()
        driver.find_element_by_id('register').click()

        wait.until(EC.presence_of_element_located((By.ID, 'batches')))
        self.assertTrue(driver.current_url == self.live_server_url + '/turnusy/')

    def test_login(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        driver.get(self.live_server_url + '/logowanie/')
        user = User.objects.filter(username="volunteer").first()
        password = 'q'
        user.set_password(password)
        user.save()

        if user is not None:
            driver.find_element_by_id('id_username').send_keys(user.username)
            driver.find_element_by_id('id_password').send_keys(password)
            button = wait.until(EC.element_to_be_clickable((By.ID, 'login_btn')))
            button.click()

        wait.until(EC.presence_of_element_located((By.ID, 'batches')))
        self.assertTrue(driver.current_url == self.live_server_url + '/turnusy/')

    def test_coordinate_login(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        driver.get(self.live_server_url + '/logowanie/')
        user = User.objects.filter(username="coordinator").first()
        password = 'q'
        user.set_password(password)
        user.save()
        coordinator_login_link = wait.until(EC.presence_of_element_located((By.ID, 'coordinator_login')))
        coordinator_login_link.click()
        wait.until(EC.presence_of_element_located((By.ID, 'login_btn')))
        self.assertTrue(driver.current_url == self.live_server_url + '/koordynator/logowanie/')

        if user is not None:
            driver.find_element_by_id('id_username').send_keys(user.username)
            driver.find_element_by_id('id_password').send_keys(password)
            button = wait.until(EC.element_to_be_clickable((By.ID, 'login_btn')))
            button.click()

        wait.until(EC.presence_of_element_located((By.ID, 'batches')))
        self.assertTrue(driver.current_url == self.live_server_url + '/koordynator/turnusy/')

    def test_nav_bar(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        driver.get(self.live_server_url)
        wait.until(EC.presence_of_element_located((By.ID, 'logo')))
        driver.find_element_by_id('logo').click()

        # events
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('Aktualności').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/aktualnosci/')

        # about us
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('O nas').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/')

        # participants
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('Podopieczni').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/')

        # volunteers
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('Wolontariusze').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/')

        # charity
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('Dobroczynność').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/')

        # contact
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('Kontakt').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/')

        # registration
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('Rejestracja').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/rejestracja/')

        # logging
        driver.find_element_by_id('logo').click()
        driver.find_element_by_link_text('Logowanie').click()
        self.assertTrue(driver.current_url == self.live_server_url + '/logowanie/')

    def test_display_batches(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        self.test_login()

        driver.find_element_by_link_text('Test').click()

        title = wait.until(EC.presence_of_element_located((By.ID, 'batch_name')))
        self.assertTrue(title.text == 'Test')

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
