import datetime
import re

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile

from components.models import Vitamin, Element, Addon
from recipes import services


class ComponentParser:
    """
    Парсер компонентов
    """
    def __init__(self, component_urls, product=None):
        self.component_urls = component_urls
        self.product = product
        self.session = requests.Session()

    def main(self):
        """
        Основной метод, определяет работу класса
        """
        for c in self.component_urls:
            url, title, photo_src, description = self.parse(c)

            if not photo_src:
                continue

            self.update_or_create_object(
                url=url,
                title=title,
                photo_src=photo_src,
                description=description,
            )
        if self.product:
            self.add_components(self.product, self.component_urls)

    def get_soup(self, url):
        """
        Возвращает объект BeautifulSoup для заданного url
        """
        r = self.session.get(url)
        return BeautifulSoup(r.text, 'lxml')

    def parse(self, url):
        """
        Парсит страницу продукта и создает объекты соответствующей модели
        """
        soup = self.get_soup(url)
        title = services.get_text_element(soup, 'h1')
        try:
            photo_src = 'https:' + services.get_image_src(soup, 'p.rtecenter img')
        except TypeError:
            photo_src = None
        description = self.get_description(
            soup,
            'div.node-content',
        )
        return url, title, photo_src, description

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

    def update_or_create_object(self, url, title, photo_src, description):
        """
        Создает/обновляет объекты соответствующей модели
        """
        model = self.get_component_model(url)
        model.objects.update_or_create(
            url=url,
            defaults={
                'title': title,
                'photo': ContentFile(
                    self.session.get(photo_src).content,
                    name=title + '.jpg',
                ),
                'description': description,
            },
        )

    @staticmethod
    def get_component_model(component_url):
        """
        Возвращает ссылку на соответствующую модель
        """
        if '/vitamin/' in component_url:
            return Vitamin
        elif '/element/' in component_url:
            return Element
        elif '/addon/' in component_url:
            return Addon

    def add_components(self, product, component_urls):
        """
        Добавляет компоненты продукту
        """
        model = self.get_component_model(component_urls[0])
        components = model.objects.filter(url__in=component_urls)
        if model == Vitamin:
            product.vitamin_set.add(*components)
        if model == Element:
            product.element_set.add(*components)
        if model == Addon:
            product.addon_set.add(*components)


def update_components(model, number, days):
    """
    Обновляет информацию о компонентах хранящихся в базе

    :param number: количество элементов обновляемых за один раз
    :param days: количество дней с последнего обновления
    """
    components = model.objects.filter(
        updated__lt=datetime.datetime.now() - datetime.timedelta(days=days)
    )[:number].values_list('url', flat=True)
    parser = ComponentParser(components)
    parser.main()


def update_vitamins(number, days):
    """
    Обновляет информацию о витаминах
    """
    update_components(Vitamin, number, days)


def update_elements(number, days):
    """
    Обновляет информацию об элементах
    """
    update_components(Element, number, days)


def update_addons(number, days):
    """
    Обновляет информацию о добавках
    """
    update_components(Addon, number, days)
