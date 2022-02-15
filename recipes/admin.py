from django.contrib import admin

from .models import (
    Recipe,
    RecipePhotoStep,
    RecipeReference,
    Tag
)


@admin.register(RecipeReference)
class RecipeReferenceAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'url',
        'is_parsed',
    ]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'id',
        'created',
        'updated',
    ]
    filter_horizontal = ['tags']


@admin.register(RecipePhotoStep)
class RecipePhotoStepAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
