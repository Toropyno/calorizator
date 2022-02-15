from django.db import models

from main.models import CoreModel


class RecipeReference(CoreModel):
    url = models.CharField(
        'URL',
        max_length=150,
        unique=True,
    )
    is_parsed = models.BooleanField(
        'Парсинг выполнен',
        default=False,
    )

    class Meta:
        verbose_name = 'Ссылка на рецепт'
        verbose_name_plural = 'Ссылки на рецепты'

    def __str__(self):
        return f'Ссылка на рецепт: {self.url}'


class Recipe(CoreModel):
    reference = models.OneToOneField(
        RecipeReference,
        on_delete=models.CASCADE,
        verbose_name='Ссылка на рецепт',
    )
    title = models.CharField(
        'Название',
        max_length=250,
    )
    photo = models.ImageField(
        'Фото',
        upload_to='recipes/Recipe/',
    )
    instruction = models.TextField(
        'Инструкция',
    )
    description = models.TextField(
        'Описание',
        blank=True,
        null=True,
    )
    author = models.CharField(
        'Автор',
        max_length=150,
    )
    serving = models.PositiveSmallIntegerField(
        'Количество порций',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тэги',
    )
    card = models.ImageField(
        'Карточка рецепта',
        upload_to='recipes/Recipe/',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_nutrition(self):
        ingredients = self.ingredient_set.all()
        calories = 0
        proteins = 0
        fats = 0
        carbohydrates = 0
        for i in ingredients:
            calories += i.product.nutrition.calories * i.weight / 100
            proteins += i.product.nutrition.protein * i.weight / 100
            fats += i.product.nutrition.fat * i.weight / 100
            carbohydrates += i.product.nutrition.carbohydrates * i.weight / 100
        return calories, proteins, fats, carbohydrates


class Tag(CoreModel):
    title = models.CharField(
        'Название',
        max_length=100,
    )
    photo = models.ImageField(
        'Фото',
        upload_to='recipes/Tag/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Тег для рецептов'
        verbose_name_plural = 'Теги для рецептов'

    def __str__(self):
        return self.title


class RecipePhotoStep(CoreModel):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    title = models.CharField(
        'Название',
        max_length=100,
    )
    photo = models.ImageField(
        'Фото',
        upload_to='recipe/RecipePhotoStep/',
    )

    class Meta:
        verbose_name = 'Пункт рецепта с фото'
        verbose_name_plural = 'Пункты рецептов с фото'
        ordering = ['id']

    def __str__(self):
        return f'{self.recipe}: {self.title}'
