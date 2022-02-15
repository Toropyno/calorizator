from django.db import models

from main.models import CoreModel
from products.models import Product


class Component(CoreModel):
    products = models.ManyToManyField(
        Product,
        verbose_name='Продукты',
    )
    url = models.CharField(
        'URL',
        max_length=150,
    )
    title = models.CharField(
        'Название',
        max_length=150,
    )
    description = models.TextField(
        'Описание',
    )

    class Meta:
        abstract = True


class Vitamin(Component):

    photo = models.ImageField(
        'Фото',
        upload_to='components/Vitamin/'
    )

    class Meta:
        verbose_name = 'Витамин'
        verbose_name_plural = verbose_name + 'ы'

    def __str__(self):
        return self.title


class Addon(Component):
    photo = models.ImageField(
        'Фото',
        upload_to='components/Addon/'
    )

    class Meta:
        verbose_name = 'Пищевая добавка'
        verbose_name_plural = 'Пищевые добавки'

    def __str__(self):
        return self.title


class Element(Component):
    photo = models.ImageField(
        'Фото',
        upload_to='components/Element/'
    )

    class Meta:
        verbose_name = 'Элемент'
        verbose_name_plural = verbose_name + 'ы'

    def __str__(self):
        return self.title
