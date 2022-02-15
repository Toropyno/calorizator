from celery import shared_task

from .services import (
    update_vitamins,
    update_addons,
    update_elements
)


# обновление информации по витаминам
@shared_task(bind=True)
def update_vitamins_task(self, number, days=5):
    update_vitamins(number, days)


# обновление информации по добавкам
@shared_task(bind=True)
def update_addons_task(self, number, days=5):
    update_addons(number, days)


# обновление информации по элементам
@shared_task(bind=True)
def update_elements_task(self, number, days=5):
    update_elements(number, days)
