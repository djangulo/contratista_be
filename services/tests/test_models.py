import os
import googlemaps
from shutil import rmtree
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from unittest.mock import patch

from accounts.models import User
from services.models import (
    Address,
    Career,
    Category,
    Company,
    Customer,
    Institution,
    Job,
    NationalId,
    Vendor,
)

TEST_IMAGE_PATH = os.path.join(
    settings.BASE_DIR, 'services/static/img/awesomeface.jpg')


class CustomerModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(
                            email='waldo@findme.com',
                            password='testpassword'
                        )
        user_one.save()
        cls.user = {
            'object': user_one,
            'email': 'waldo@findme.com',
            'password': 'testpassword'
        }

    def test_cannot_create_customer_without_user(self):
        customer = Customer(
            first_name='Waldo',
            last_name='The Unfindable',
            display_name='waldo',
            primary_phone='5555555555',
            secondary_phone='1234567893'
        )
        self.assertRaises(ValidationError, customer.save)
    
    def test_can_create_customer_with_user(self):
        customer = Customer.objects.create(
            first_name='Waldo',
            last_name='The Unfindable',
            display_name='waldo',
            primary_phone='5555555555',
            secondary_phone='1234567893',
            user=self.user['object']
        )
        self.assertEqual(Customer.objects.first().user.email, 'waldo@findme.com')

    def test_picture_uploads_successfully(self):
        customer = Customer.objects.create(
            first_name='Waldo',
            last_name='The Unfindable',
            display_name='waldo',
            primary_phone='5555555555',
            secondary_phone='1234567893',
            picture=SimpleUploadedFile(
                name='my_awesome_face.jpg',
                content=open(TEST_IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg'
            ),
            user=self.user['object']
        )
        self.assertIn(
            'my_awesome_face.jpg',
            os.listdir(
                os.path.join(
                    settings.MEDIA_ROOT,
                    'users',
                    f'user_{self.user["object"].id}'
                )
            )            
        )

    def test_reverse_relation_to_user_model(self):
        customer = Customer.objects.create(
            first_name='Waldo',
            last_name='The Unfindable',
            display_name='waldo',
            primary_phone='5555555555',
            secondary_phone='1234567893',
            picture=SimpleUploadedFile(
                name='my_awesome_face.jpg',
                content=open(TEST_IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg'
            ),
            user=self.user['object']
        )
        self.assertEqual(customer.user, self.user['object'])
    

class AddressModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
                            email='waldo@findme.com',
                            password='testpassword'
                        )
        user.save()
        customer = Customer.objects.create(
            first_name='Waldo',
            last_name='The Unfindable',
            display_name='waldo',
            primary_phone='5555555555',
            secondary_phone='1234567893',
            picture=SimpleUploadedFile(
                name='my_awesome_face.jpg',
                content=open(TEST_IMAGE_PATH, 'rb').read(),
                content_type='image/jpeg'
            ),
            user=user
        )
        cls.customer = customer

    def test_cannot_create_address_without_customer(self):
        address = Address(
            full_name='My first address',
            state_province_region='Santo Domingo',
            city='DN',
            sector='Los Cacicazgos',
            address_line_one='c/ Hatuey',
            phone_number='5555555555',
            is_primary=False
        )
        self.assertRaises(ValidationError, address.save)

    def test_can_create_address_with_customer(self):
        address = Address.objects.create(
            full_name='My first address',
            state_province_region='Santo Domingo',
            city='DN',
            sector='Los Cacicazgos',
            address_line_one='c/ Hatuey',
            phone_number='5555555555',
            is_primary=False,
            owner=self.customer
        )
        self.assertEqual(
            Address.objects.first().full_name,
            address.full_name
        )

    @patch('googlemaps.Client.geocode')
    def test_geocode_is_called_properly(self, mock_geocode):
        address = Address.objects.create(
            full_name='My first address',
            state_province_region='Santo Domingo',
            city='DN',
            sector='Los Cacicazgos',
            address_line_one='c/ Hatuey, no. 102',
            phone_number='5555555555',
            is_primary=False,
            owner=self.customer
        )
        print(address.address_line_two)

        gmaps = googlemaps.Client(key=settings.GOOGLEMAPS_SECRET_KEY)
        gmaps.geocode('c/ Hatuey, no. 102, Los Cacicazgos, Santo Domingo, Dominican Republic')

        self.assertTrue(mock_geocode.called)


    @patch('googlemaps.Client.geocode')
    def test_address_is_geocoded_properly(self, mock_geocode):
        address = Address.objects.create(
            full_name='My first address',
            state_province_region='Santo Domingo',
            city='DN',
            sector='Los Cacicazgos',
            address_line_one='c/ Hatuey, no. 102',
            phone_number='5555555555',
            is_primary=False,
            owner=self.customer
        )
        print(address.address_line_two)

        gmaps = googlemaps.Client(key=settings.GOOGLEMAPS_SECRET_KEY)
        gmaps.geocode('c/ Hatuey, no. 102, Los Cacicazgos, Santo Domingo, Dominican Republic')

        self.assertTrue(mock_geocode.called)
        self.assertEqual(
            'c/ Hatuey, no. 102, Los Cacicazgos, DN, Santo Domingo, Dominican Republic',
            address.formatted_name
        )

