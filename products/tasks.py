from celery import shared_task

from .services import update_products


# обновление информации о продуктах
@shared_task(bind=True)
def update_products_task(self, number, days=5):
    update_products(number, days)
