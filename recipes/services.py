import datetime
import re
import requests

from bs4 import BeautifulSoup
from django.core.files.base import ContentFile

from products.models import Ingredient, Product
from products.services import ProductParser
from recipes.models import RecipeReference, RecipePhotoStep, Recipe, Tag


def get_text_element(soup, selector):
    """
    Из объекта BeautifulSoup возвращает текстовое значение
     элемента определенного селектором selector
    """
    element = soup.select_one(selector)
    try:
        value = element.text.strip()
    except AttributeError:
        value = None
    return value


def get_image_src(soup, selector):
    """
    Из объекта BeautifulSoup возвращает значение атрибута src
     элемента определенного селектором selector
    """
    element = soup.select_one(selector)
    try:
        src = element.get('src')
    except AttributeError:
        src = None
    return src


class RecipeReferencesCrawler:
    """
    Сбор ссылок на рецепты
    """
    def __init__(self, limit=10, base_url='https://calorizator.ru'):
        self.limit = limit
        self.base_url = base_url
        self.session = requests.Session()

    def main(self):
        """
        Основной метод, определяет работу класса
        """
        page_urls = self.get_sitemap_pages(self.base_url + 'sitemap.xml')
        urls = self.crawl_recipes(page_urls, self.limit)
        for url in urls:
            RecipeReference.objects.get_or_create(url=url)

    def get_soup(self, url):
        """
        Возвращает объект BeautifulSoup для заданного url
        """
        r = self.session.get(url)
        return BeautifulSoup(r.text, 'lxml')

    def get_sitemap_pages(self, sitemap_url):
        """
        Возвращает список url-адресов страниц с карты сайта
        """
        soup = self.get_soup(sitemap_url)
        sitemap_page_elems = soup.select('sitemap>loc')
        sitemap_page_urls = [item.text.strip() for item in sitemap_page_elems]
        return sitemap_page_urls

    def crawl_recipes(self, page_urls, limit=None):
        """
        Обходит страницы карты сайта, собирает url-адреса рецептов и возвращает их в виде списка

        :param limit: ограничивает количество рецептов
        :param page_urls: список url-адресов страниц с карты сайта
        """
        urls = []

        for url in page_urls:
            soup = self.get_soup(url)
            recipes = soup.find_all(text=re.compile('recipes'), limit=limit)
            urls.extend(recipes)
        return urls


class RecipeParser:
    """
    Парсер рецептов
    """
    def __init__(self, reference_list, base_url='https://calorizator.ru'):
        self.reference_list = reference_list
        self.base_url = base_url
        self.session = requests.Session()

    def main(self):
        """
        Основной метод, определяет работу класса
        """
        for r in self.reference_list:
            self.parse(r)

    def get_soup(self, url):
        """
        Возвращает объект BeautifulSoup для заданного url
        """
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def parse(self, reference):
        """
        Парсит страницу рецепта, создает объект рецепта и связанные с ним объекты
        """
        soup = self.get_soup(reference.url)

        # парсим необходимые атрибуты
        title = get_text_element(
            soup,
            'h1#page-title',
        )
        instruction = get_text_element(
            soup,
            'div[itemprop="recipeInstructions"] ol',
        )
        description = get_text_element(
            soup,
            'div[itemprop="description"] p',
        )
        author = get_text_element(
            soup,
            'div.recipes-author span',
        )
        serving = get_text_element(
            soup,
            'span[itemprop="recipeYield"]',
        )
        photo_src = get_image_src(
            soup,
            '.field.field-type-filefield.field-field-picture img',
        )
        card_src = get_image_src(
            soup,
            'p.recipes-card img',
        )
        photo_steps = self.get_photo_steps(
            soup,
            '#galleria a',
        )
        ingredients = self.get_ingredients(
            soup,
            '#ar_tabl tbody tr',
            ProductParser,
        )
        tags = self.get_tags(
            soup,
            '#recipes-col2 a',
        )

        # Создаем/обновляем рецепт
        recipe, _ = Recipe.objects.update_or_create(
            reference=reference,
            defaults={
                'title': title,
                'instruction': instruction,
                'description': description,
                'author': author,
                'serving': serving,
                'photo': ContentFile(
                    self.session.get(photo_src).content,
                    name=title + '.jpg',
                ),
                'card': ContentFile(
                    self.session.get(card_src).content,
                    name='card_' + title + '.jpg',
                ),
            }
        )
        # Добавляем теги к рецепту
        recipe.tags.add(*tags)

        # Создаем пошаговую инструкцию
        self.set_photo_steps(
            recipe,
            photo_steps,
        )

        # Создаем ингредиенты
        self.set_ingredients(
            recipe,
            ingredients,
        )
        reference.is_parsed = True
        reference.save()

    def set_photo_steps(self, recipe, step_list):
        """
        Добавляет к рецепту recipe пошаговую инструкцию с фото из step_list
        """
        for title, href in step_list:
            RecipePhotoStep.objects.update_or_create(
                recipe=recipe,
                title=title,
                defaults={
                    'photo': ContentFile(
                        self.session.get(href).content,
                        name=title + '.jpg',
                    ),
                }
            )

    @staticmethod
    def set_ingredients(recipe, ingredient_list):
        """
        Создает объекты Ingredient для списка recipe на основе полученного
         списка ингредиентов ingredient_list
        """
        for i in ingredient_list:
            product_url, measure, weight = i
            product = Product.objects.get(url=product_url)
            Ingredient.objects.update_or_create(
                recipe=recipe,
                product=product,
                defaults={
                    'measure': measure,
                    'weight': weight,
                }
            )

    def get_ingredients(self, soup, selector, parser=None):
        """
        Из объекта BeautifulSoup возвращает список кортежей с описанием ингредиентов
         по заданному селектору selector
        """
        ingredient_list = []
        product_urls = []

        ingredient_elems = soup.select(selector)
        for ingredient in ingredient_elems:
            product_url = self.base_url + ingredient.select_one('a').get('href')
            measure = ingredient.contents[3].text.strip()
            weight = ingredient.contents[5].text.strip()

            product_urls.append(product_url)
            ingredient_list.append((product_url, measure, weight))

        # парсим продукты
        if parser:
            p = ProductParser(product_urls)
            p.main()
        return ingredient_list

    @staticmethod
    def get_photo_steps(soup, selector):
        """
        Из объекта BeautifulSoup возвращает список фотографий (src) пунктов рецепта
         по заданному селектору selector
        """
        steps = []
        step_elems = soup.select(selector)
        for e in step_elems:
            title = e.select_one('img').get('alt')
            href = e.get('href')
            steps.append((title, href))
        return steps

    @staticmethod
    def get_tags(soup, selector):
        """
        Из объекта BeautifulSoup получает список тегов для рецепта по заданному селектору selector
        Создает по необходимости объекты Tag на основе полученных тегов

        Возвращает список объектов Tag соответствующих полученным тегам
        """
        tags = []
        tag_elems = soup.select(selector)

        for t in tag_elems:
            tag, _ = Tag.objects.get_or_create(
                title=t.text,
            )
            tags.append(tag)
        return tags


def update_recipes(number, days):
    """
    Обновляет рецепты

    :param number: количество элементов обновляемых за один раз
    :param days: количество дней с последнего обновления
    """
    recipes = Recipe.objects.filter(
        updated__lt=datetime.datetime.now() - datetime.timedelta(days=days)
    )[:number]
    references = recipes.values_list('reference__url', flat=True)
    parser = RecipeParser(references)
    parser.main()
