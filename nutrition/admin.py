from django.contrib import admin

from .models import ProductNutrition


@admin.register(ProductNutrition)
class ProductNutritionAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'calories',
        'proteins',
        'fats',
        'carbohydrates',
    ]
