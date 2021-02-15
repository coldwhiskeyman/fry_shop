from django.contrib import admin

from shops.models import (
    CartLine,
    Product,
    Promotion,
    Purchase,
    Shop
)


class ProductInLine(admin.TabularInline):
    model = Product


class PromotionInLine(admin.TabularInline):
    model = Promotion


class CartInLine(admin.TabularInline):
    model = CartLine


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    inlines = [ProductInLine, PromotionInLine]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'shop']


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    pass


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['cost', 'user', 'shop']
    inlines = [CartInLine]
