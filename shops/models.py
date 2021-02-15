from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.models import User


class Shop(models.Model):
    name = models.CharField(_('Название'), max_length=100)

    class Meta:
        verbose_name = _("магазин")
        verbose_name_plural = _("магазины")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop_details', kwargs={'pk': self.pk})


class Product(models.Model):
    name = models.CharField(_('Название'), max_length=100)
    price = models.IntegerField(_('Цена'))
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='products', verbose_name=_('Магазин'))

    class Meta:
        verbose_name = _("товар")
        verbose_name_plural = _("товары")

    def __str__(self):
        return self.name


class Promotion(models.Model):
    name = models.CharField(_('Название'), max_length=100)
    text = models.TextField(_('Текст'))
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='promotions', verbose_name=_('Магазин'))
    condition = models.TextField(_('Условие'), null=True)
    discount = models.TextField(_('Скидка'), null=True)

    class Meta:
        verbose_name = _("промоакция")
        verbose_name_plural = _("промоакции")

    def __str__(self):
        return self.name


class Purchase(models.Model):
    cost = models.IntegerField(_('Сумма'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases', verbose_name=_('Покупатель'))
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, related_name='purchases', verbose_name=_('Магазин'))
    complete = models.BooleanField(_('Совершено'), default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("покупка")
        verbose_name_plural = _("покупки")

    def __str__(self):
        return _(f'Покупка в магазине {self.shop} на сумму {self.cost}')


class CartLine(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE, related_name='cart', verbose_name=_('Покупка'))
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name=_('Товар'))
    quantity = models.IntegerField(_('Количество'), default=1)

    class Meta:
        verbose_name = _("позиция")
        verbose_name_plural = _("позиции")

    def __str__(self):
        return self.product
