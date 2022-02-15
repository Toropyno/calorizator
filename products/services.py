import datetime
import re

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile

from components import services
from nutrition.models import ProductNutrition
from products.models import Product
from recipes import services


class ProductParser:
    """
    Парсер продуктов
    """
    def __init__(self, product_urls, base_url='https://calorizator.ru'):
        self.session = requests.Session()
        self.base_url = base_url
        self.product_urls = product_urls

    def main(self):
        """
        Основной метод, определяет работу класса
        """
        for p in self.product_urls:
            self.parse(p)

    def get_soup(self, url):
        """
        Возвращает объект BeautifulSoup для заданного url
        """
        r = self.session.get(url)
        return BeautifulSoup(r.text, 'lxml')

    def parse(self, url):
        """
        Парсит страницу продукта и создает объекты Product
        """
        soup = self.get_soup(url)

        # парсим необходимые поля
        title = services.get_text_element(
            soup,
            'h1#page-title',
        )
        photo_src = services.get_image_src(
            soup,
            '.field.field-type-filefield.field-field-picture img',
        )
        description = self.get_description(
            soup,
            'div.node-content',
        )
        calories, proteins, fats, carbohydrates = self.get_nutrition(
            soup,
            '.fieldgroup.group-base .field-label-inline-first',
        )

        # создаем/обновляем продукт
        product, _ = Product.objects.update_or_create(
            url=url,
            defaults={
                'title': title,
                'photo': ContentFile(
                    self.session.get(photo_src).content,
                    name=title + '.jpg',
                ),
                'description': description,
            }
        )
        # создаем/обновляем пищевую ценность продукта
        ProductNutrition.objects.update_or_create(
            product=product,
            defaults={
                'calories': calories,
                'proteins': proteins,
                'fats': fats,
                'carbohydrates': carbohydrates,
            }
        )

        self.check_components(soup, '/vitamin/', product)
        self.check_components(soup, '/element/', product)
        self.check_components(soup, '/addon/', product)

    def check_components(self, soup, pattern, product=None):
        """
        Проверяет наличие компонентов на странице продукте

        Если компоненты присутствуют, то парсит их (ComponentParser)
         и добавляет к нужному продукту (self.add_components)
        """
        urls = []
        content = soup.select_one('.node-content')
        components = content.find_all('a', href=re.compile(pattern))
        if components:
            for c in components:
                href = c.get('href')
                if href.startswith('//'):
                    url = 'https:' + href
                else:
                    url = self.base_url + href
                urls.append(url)

            if product:
                component_parser = services.ComponentParser(urls, product=product)
                component_parser.main()
        return urls

    @staticmethod
    def add_components(product, component_urls):
        """
        К соответствующему продукту добавляет компоненты
        """
        components = []
        c1 = component_urls[0]
        if '/vitamin/' in c1:
            product.vitamin_set.add(*components)
        elif '/element/' in c1.url:
            product.element_set_set.add(*components)
        elif '/addon/' in c1.url:
            product.addon_set_set.add(*components)

    @staticmethod
    def get_description(soup, selector):
        """
        Из объекта BeautifulSoup возвращает описание продукта
        """
        description = ''
        description_elems = soup.select_one(selector).find_all(re.compile('h3|p'))
        for d in description_elems:
            description += d.text
        return description

    @staticmethod
    def get_nutrition(soup, selector):
        """
        Из объекта BeautifulSoup возвращает пищевую ценность продукта (калории, белки, жиры, углеводы)
        """
        nutrition_elems = soup.select(selector)
        calories = nutrition_elems[0].next_sibling.strip()
        proteins = nutrition_elems[1].next_sibling.strip()
        fats = nutrition_elems[2].next_sibling.strip()
        carbohydrates = nutrition_elems[3].next_sibling.strip()
        return calories, proteins, fats, carbohydrates


def update_products(number, days):
    """
    Обновляет информацию о продуктах

    :param number: количество элементов обновляемых за один раз
    :param days: количество дней с последнего обновления
    """
    products = Product.objects.filter(
        updated__lt=datetime.datetime.now() - datetime.timedelta(days=days)
    )[:number].values_list('url', flat=True)
    parser = ProductParser(products)
    parser.main()
