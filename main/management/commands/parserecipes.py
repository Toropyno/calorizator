from django.core.management import BaseCommand

from recipes.models import RecipeReference
from recipes.services import RecipeParser


class Command(BaseCommand):
    """
    Парсит рецепты
    """
    def handle(self, *args, **options):
        references = RecipeReference.objects.filter(is_parsed=False)[:3]
        parser = RecipeParser(references)
        parser.main()
