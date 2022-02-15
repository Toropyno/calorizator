from django.core.management import BaseCommand

from recipes.services import RecipeReferencesCrawler


class Command(BaseCommand):
    """
    Собирает ссылки на рецепты с карты сайта
    """
    def handle(self, *args, **options):
        crawler = RecipeReferencesCrawler()
        crawler.main()
