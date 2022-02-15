from django.contrib import admin

from .models import Element, Addon, Vitamin


class ComponentAdmin:
    list_display = [
        'title',
        'id',
        'updated',
    ]
    filter_horizontal = ['products']


@admin.register(Element)
class ElementAdmin(ComponentAdmin, admin.ModelAdmin):
    pass


@admin.register(Addon)
class AddonAdmin(ComponentAdmin, admin.ModelAdmin):
    pass


@admin.register(Vitamin)
class VitaminAdmin(ComponentAdmin, admin.ModelAdmin):
    pass
