from django.db import models

from main.models import CoreModel
from recipes.models import Recipe


class Product(CoreModel):
    url = models.CharField(
        'URL',
        max_length=150,
        unique=True,
    )
    title = models.CharField(
        'Название',
        max_length=250,
    )
    photo = models.ImageField(
        'Фото',
        upload_to='products/Product/',
    )
    description = models.TextField(
        'Описание',
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['title']

    def __str__(self):
        return self.title


class Ingredient(CoreModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
    )
    measure = models.CharField(
        'Мера',
        max_length=30,
    )
    weight = models.FloatField(
        'Вес',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.product} для {self.recipe}'
