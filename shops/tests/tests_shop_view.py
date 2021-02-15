from django.test import TestCase

from shops.models import Product, Promotion, Shop


class ShopViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        shop1 = Shop.objects.create(name='Пятерочка')
        shop2 = Shop.objects.create(name='Красное и Белое')

        product1 = Product.objects.create(name='Картошка', price=30, shop=shop1)
        product2 = Product.objects.create(name='Макароны', price=80, shop=shop1)

        promotion = Promotion.objects.create(name='Распродажа картошки',
                                             text='3 мешка картошки по цене 2!', shop=shop1)

    def test_view_shop_list(self):
        response = self.client.get('/shops/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shops/shop_list.html')
        self.assertEqual(len(response.context['shop_list']), 2)
        self.assertContains(response, 'Пятерочка')

    def test_view_blog_detail(self):
        response = self.client.get('/shops/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shops/shop_detail.html')
        self.assertEqual(response.context['object'].id, 1)
        self.assertContains(response, 'Пятерочка')

    def test_view_products_in_shop(self):
        response = self.client.get('/shops/1')
        shop = Shop.objects.get(id=1)
        self.assertEqual(len(shop.products.all()), 2)
        self.assertContains(response, 'Картошка')

    def test_view_promotions_in_shop(self):
        response = self.client.get('/shops/1')
        self.assertContains(response, '3 мешка картошки по цене 2!')
