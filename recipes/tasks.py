from celery import shared_task

from recipes.models import RecipeReference
from .services import (
    RecipeParser,
    RecipeReferencesCrawler,
    update_recipes
)


# сбор ссылок на рецепты
@shared_task(bind=True)
def crawl_references(self, number):
    crawler = RecipeReferencesCrawler(limit=number)
    crawler.main()


# парсинг рецептов
@shared_task(bind=True)
def parse_recipes_task(self, number):
    references = RecipeReference.objects.filter(is_parsed=False)[:number]
    parser = RecipeParser(references)
    parser.main()


# обновление рецептов
@shared_task(bind=True)
def update_recipes_task(self, number, days=5):
    update_recipes(number, days)
