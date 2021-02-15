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
        user = User.objects.create_user('user', password='Qwerty123', balance=1000)

        shop = Shop.objects.create(name='Пятерочка')
        promotion = Promotion.objects.create(name='Распродажа картошки',
                                             text='3 мешка картошки по цене 2!',
                                             shop=shop,
                                             condition="{}['Картошка'] >= 3",
                                             discount='{} - 30',
                                             )
        Product.objects.create(name='Картошка', price=30, shop=shop)
        Product.objects.create(name='Макароны', price=80, shop=shop)

    def test_view_cart(self):
        self.client.login(username='user', password='Qwerty123')
        potato = Product.objects.get(name='Картошка')
        noodles = Product.objects.get(name='Макароны')
        user = User.objects.get_by_natural_key('user')
        shop = Shop.objects.get(name='Пятерочка')
        purchase = Purchase.objects.create(cost=110, user=user, shop=shop, complete=False)
        CartLine.objects.create(purchase=purchase, product=potato, quantity=1)
        CartLine.objects.create(purchase=purchase, product=noodles, quantity=1)
        response = self.client.get('/shops/1/cart')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shops/cart_detail.html')
        self.assertContains(response, 'Картошка - 1 шт.')
        self.assertContains(response, 110)
        self.assertContains(response, 'Пятерочка')

    def test_view_empty_cart(self):
        self.client.login(username='user', password='Qwerty123')
        response = self.client.get('/shops/1/cart')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shops/cart_detail.html')
        self.assertContains(response, 'Ваша корзина пуста')

    def test_create_cart(self):
        self.client.login(username='user', password='Qwerty123')
        potato = Product.objects.get(name='Картошка')
        self.client.post(f'/shops/add_to_cart/{potato.id}', data={'quantity': 1})
        self.assertEqual(len(Purchase.objects.all()), 1)
        response = self.client.get('/shops/1/cart')
        self.assertContains(response, 'Картошка - 1 шт.')
        self.assertContains(response, 30)

    def test_add_to_cart(self):
        self.client.login(username='user', password='Qwerty123')
        user = User.objects.get_by_natural_key('user')
        shop = Shop.objects.get(name='Пятерочка')
        potato = Product.objects.get(name='Картошка')
        purchase = Purchase.objects.create(cost=30, user=user, shop=shop, complete=False)
        CartLine.objects.create(purchase=purchase, product=potato, quantity=1)
        noodles = Product.objects.get(name='Макароны')
        self.client.post(f'/shops/add_to_cart/{noodles.id}', data={'quantity': 1})
        response = self.client.get('/shops/1/cart')
        self.assertContains(response, 'Картошка - 1 шт.')
        self.assertContains(response, 'Макароны - 1 шт.')
        self.assertContains(response, 110)

    def test_purchase_success(self):
        self.client.login(username='user', password='Qwerty123')
        user = User.objects.get_by_natural_key('user')
        shop = Shop.objects.get(name='Пятерочка')
        potato = Product.objects.get(name='Картошка')
        purchase = Purchase.objects.create(cost=30, user=user, shop=shop, complete=False)
        CartLine.objects.create(purchase=purchase, product=potato, quantity=1)
        self.client.post('/shops/1/cart/confirm')
        user = User.objects.get_by_natural_key('user')
        self.assertEqual(user.balance, 970)
        self.assertEqual(len(user.purchases.all()), 1)

    def test_remove_incomplete_purchase(self):
        pass

    def test_apply_promotions(self):
        self.client.login(username='user', password='Qwerty123')
        user = User.objects.get_by_natural_key('user')
        shop = Shop.objects.get(name='Пятерочка')
        potato = Product.objects.get(name='Картошка')
        purchase = Purchase.objects.create(cost=60, user=user, shop=shop, complete=False)
        CartLine.objects.create(purchase=purchase, product=potato, quantity=2)
        self.client.post(f'/shops/add_to_cart/{potato.id}', data={'quantity': 1})
        purchase = Purchase.objects.get(user=user, shop=shop, complete=False)
        self.assertEqual(purchase.cost, 60)
