from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthApiTests(APITestCase):
    def test_user_can_register(self):
        response = self.client.post('/api/register/', {
            'username': 'aman',
            'email': 'aman@example.com',
            'password': 'strong-pass-123',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'aman@example.com')
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.filter(email='aman@example.com').exists())

    def test_user_can_login_with_email_and_receive_jwt(self):
        User.objects.create_user(
            username='aman',
            email='aman@example.com',
            password='strong-pass-123',
        )

        response = self.client.post('/api/login/', {
            'email': 'aman@example.com',
            'password': 'strong-pass-123',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_update_is_limited_to_owner(self):
        owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='strong-pass-123',
        )
        stranger = User.objects.create_user(
            username='stranger',
            email='stranger@example.com',
            password='strong-pass-123',
        )
        self.client.force_authenticate(user=stranger)

        response = self.client.patch(f'/api/users/{owner.id}/', {'bio': 'changed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

# Create your tests here.
