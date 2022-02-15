from django.db import models

from main.models import CoreModel
from products.models import Product
from recipes.models import Recipe


class Nutrition(CoreModel):
    proteins = models.FloatField(
        'Количество белка',
    )
    fats = models.FloatField(
        'Количество жиров',
    )
    carbohydrates = models.FloatField(
        'Количество углеводов',
    )
    calories = models.FloatField(
        'Количество калорий',
    )

    class Meta:
        abstract = True


class ProductNutrition(Nutrition):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='nutrition',
    )

    class Meta:
        verbose_name = 'Пищевая ценность продукта'
        verbose_name_plural = 'Пищевая ценность продуктов'

    def __str__(self):
        return f'Пищевая ценность продукта: {self.product}'
