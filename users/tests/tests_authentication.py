from django.test import TestCase

from users.models import User


class UserAuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('user', password='Qwerty123')

    def test_authentication_success(self):
        data = {
            'username': 'user',
            'password': 'Qwerty123',
        }
        response = self.client.post('/users/login', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_authentication_wrong_password(self):
        data = {
            'username': 'user',
            'password': 'Qwerty1234',
        }
        response = self.client.post('/users/login', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пожалуйста, введите правильные имя пользователя и пароль')

    def test_authentication_user_not_registered(self):
        data = {
            'username': 'Vasya',
            'password': 'Qwerty123',
        }
        response = self.client.post('/users/login', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пожалуйста, введите правильные имя пользователя и пароль')
        with self.assertRaises(User.DoesNotExist):
            User.objects.get_by_natural_key('Vasya')
