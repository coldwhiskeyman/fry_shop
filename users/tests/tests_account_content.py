from django.contrib.auth.models import User
from django.test import TestCase

from shops.models import (
    CartLine,
    Product,
    Promotion,
    Purchase,
    Shop
)
from users.models import User


class UserAuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('user', password='Qwerty123', first_name='Ivan', last_name='Ivanov', balance=1000)
        User.objects.create_user('another_user', password='Qwerty123')

        shop = Shop.objects.create(name='Пятерочка')
        promotion = Promotion.objects.create(name='Распродажа картошки',
                                             text='3 мешка картошки по цене 2!', shop=shop)
        Product.objects.create(name='Картошка', price=30, shop=shop)
        Product.objects.create(name='Макароны', price=80, shop=shop)

    def test_view_account(self):
        self.client.login(username='user', password='Qwerty123')
        response = self.client.get('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_detail.html')
        self.assertEqual(response.context['object'].id, 1)
        self.assertContains(response, 'Ivan')

    def test_view_account_unregistered(self):
        response = self.client.get('/users/1')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/users/login?next=/users/1')

    def test_balance_deposit(self):
        self.client.login(username='user', password='Qwerty123')
        response = self.client.get('/users/1')
        self.assertContains(response, '1000 &#8381;')
        self.client.post('/users/1/deposit', data={'amount': 100})
        response = self.client.get('/users/1')
        self.assertContains(response, '1100 &#8381;')

    def test_view_promotions(self):
        self.client.login(username='user', password='Qwerty123')
        response = self.client.get('/users/1')
        self.assertContains(response, 'Пятерочка')
        self.assertContains(response, '3 мешка картошки по цене 2!')

    def test_view_purchase_history(self):
        self.client.login(username='user', password='Qwerty123')
        response = self.client.get('/users/1')
        self.assertEqual(len(response.context['purchase_history']), 0)
        potato = Product.objects.get(name='Картошка')
        noodles = Product.objects.get(name='Макароны')
        user = User.objects.get_by_natural_key('user')
        shop = Shop.objects.get(name='Пятерочка')
        purchase = Purchase.objects.create(cost=110, user=user, shop=shop, complete=True)
        CartLine.objects.create(purchase=purchase, product=potato, quantity=1)
        CartLine.objects.create(purchase=purchase, product=noodles, quantity=1)
        response = self.client.get('/users/1')
        self.assertEqual(len(response.context['purchase_history']), 1)
        self.assertContains(response, 'Картошка - 1 шт.')
        self.assertContains(response, 110)
        self.assertContains(response, 'Пятерочка')
