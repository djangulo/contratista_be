from django.conf import settings
from django.urls import reverse
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from accounts.models import User

AUTH_THROTTLE_RATE = int(settings.REST_FRAMEWORK[
    'DEFAULT_THROTTLE_RATES']['authtoken'].split('/')[0])

class AccountAPITests(APITestCase):
    TESTING_THRESHOLD = '100/min'

    @classmethod
    def setUpTestData(cls):
        user_one = User.objects.create_user(
                            email='merida@kingdom.com',
                            password='testpassword'
                        )
        user_one.save()
        cls.user1 = {
            'user': user_one,
            'email': 'merida@kingdom.com',
            'password': 'testpassword'
        }
        cls.token1 = Token.objects.get(user_id=1)

    def test_user_can_retrieve_token(self):
        token = str(self.token1)
        url = reverse('get-token')
        response = self.client.post(url, data={
            'email': self.user1['email'],
            'password': self.user1['password']
        })
        self.assertEqual(response.data['token'], token)
    
    def test_token_rebound_on_credential_failure(self):
        url = reverse('get-token')
        response = self.client.post(url, data={
            'email': 'phney@email.com',
            'password': 'phoneypassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Unable to log in with provided credentials.",
            response.data['non_field_errors']
        )
