from django.views.decorators.cache import cache_page
from django.urls import path

from shops.views import (
    AddToCartView,
    CartDetailView,
    ConfirmPurchaseView,
    ShopDetailView,
    ShopListView
)


urlpatterns = [
    path('', cache_page(600)(ShopListView.as_view()), name='shop_list'),
    path('<int:pk>', cache_page(600)(ShopDetailView.as_view()), name='shop_detail'),
    path('<int:pk>/cart', CartDetailView.as_view(), name='cart_detail'),
    path('add_to_cart/<int:product>', AddToCartView.as_view(), name='add_to_cart'),
    path('<int:pk>/cart/confirm', ConfirmPurchaseView.as_view(), name='confirm_purchase'),
]
