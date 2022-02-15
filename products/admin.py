from django.contrib import admin

from .models import Product, Ingredient


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'id',
        'updated',
    ]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'id',
        'product',
        'measure',
        'weight',
    ]
    ordering = [
        'product__title',
    ]
