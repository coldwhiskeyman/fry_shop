from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView

from shops.forms import AddToCartForm
from shops.models import CartLine, Product, Promotion, Purchase, Shop


def apply_promotion(purchase, promotion):
    cart_dict = {line.product.name: line.quantity for line in purchase.cart.all()}
    applied = eval(promotion.condition.format(cart_dict))
    if applied:
        purchase.cost = eval(promotion.discount.format(purchase.cost))
        purchase.save()


class ShopListView(ListView):
    model = Shop


class ShopDetailView(DetailView):
    model = Shop

    def get_context_data(self, **kwargs):
        context = super(ShopDetailView, self).get_context_data(**kwargs)
        context['form'] = AddToCartForm()
        return context


class CartDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'shops/cart_detail.html'
    login_url = '/users/login'

    def get(self, request, *args, **kwargs):
        try:
            Purchase.objects.get(user=self.request.user, shop_id=self.kwargs['pk'], complete=False)
            return super(CartDetailView, self).get(request, *args, **kwargs)
        except Purchase.DoesNotExist:
            return render(request, 'shops/cart_detail.html', {'empty_cart': True})

    def get_context_data(self, **kwargs):
        context = super(CartDetailView, self).get_context_data(**kwargs)
        context['object'] = Purchase.objects.get(user=self.request.user, shop_id=self.kwargs['pk'], complete=False)
        return context


class AddToCartView(FormView):
    form_class = AddToCartForm

    def form_valid(self, form):
        product = Product.objects.get(id=self.kwargs['product'])
        if self.request.POST['quantity']:
            quantity = int(self.request.POST['quantity'])
        else:
            quantity = 1
        purchase, _created = Purchase.objects.get_or_create(
            user=self.request.user, shop=product.shop, complete=False,
            defaults={'cost': 0},
        )
        add_line, created = CartLine.objects.get_or_create(purchase=purchase, product=product)
        if created:
            add_line.quantity = quantity
        else:
            add_line.quantity += quantity
        add_line.save()
        purchase.cost = 0
        for line in purchase.cart.all():
            purchase.cost += line.product.price * line.quantity
        purchase.save()
        promotions = Promotion.objects.filter(shop=product.shop)
        for promotion in promotions.all():
            apply_promotion(purchase, promotion)
        url = reverse('shop_detail', kwargs={'pk': product.shop.id})
        messages.success(self.request, _(f'Добавлено в корзину: {product}'))
        return redirect(url)


class ConfirmPurchaseView(View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        shop = Shop.objects.get(id=kwargs['pk'])
        purchase = Purchase.objects.get(user=user, shop=shop, complete=False)
        user.balance -= purchase.cost
        user.save()
        purchase.complete = True
        purchase.save()

        key = make_template_fragment_key('purchases')
        cache.delete(key)

        url = reverse('user_detail', kwargs={'pk': user.id})
        return redirect(url)
