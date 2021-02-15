from django.test import TestCase

from users.models import User


class UserRegistrationTests(TestCase):
    def test_registration_success(self):
        data = {
            'username': 'user',
            'first_name': 'Ivan',
            'last_name': 'Ivanov',
            'password1': 'Very1Secret2Password3',
            'password2': 'Very1Secret2Password3',
        }
        response = self.client.post('/users/register', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'user')
        self.assertEqual(users[0].first_name, 'Ivan')
        self.assertEqual(users[0].balance, 0)

    def test_registration_fail(self):
        data = {
            'username': 'user',
            'password1': 'Very1Secret2Password3',
            'password2': 'Very4Secret5Password6',
        }
        response = self.client.post('/users/register', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        users = User.objects.all()
        self.assertEqual(len(users), 0)
        self.assertContains(response, 'Два поля с паролями не совпадают')
