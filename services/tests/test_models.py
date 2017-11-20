import os
from shutil import rmtree
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

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
            name='Waldo The Unfindable',
            display_name='waldo',
            primary_phone='5555555555',
            secondary_phone='1234567893'
        )
        self.assertRaises(ValidationError, customer.save)
    
    def test_can_create_customer_with_user(self):
        customer = Customer.objects.create(
            name='Waldo The Unfindable',
            display_name='waldo',
            primary_phone='5555555555',
            secondary_phone='1234567893',
            user=self.user['object']
        )
        self.assertEqual(Customer.objects.first().user.email, 'waldo@findme.com')

    def test_picture_uploads_successfully(self):
        customer = Customer.objects.create(
            name='Waldo The Unfindable',
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
            name='Waldo The Unfindable',
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
    

class AdressModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(
                            email='waldo@findme.com',
                            password='testpassword'
                        )
        user_one.save()
        user_two = User.objects.create_user(
                            email='alexander@macedon.com',
                            password='testpassword'
                        )
        user_two.save(),
        cls.user1 = {
            'user': user_one,
            'email': 'waldo@findme.com',
            'password': 'testpassword'
        }
        cls.user2 = {
            'user': user_two,
            'email': 'alexanderr@macedon.com',
            'password': 'testpassword'
        }