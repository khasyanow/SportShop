from decimal import Decimal
from django.test import TestCase
from catalog.models import Category, Product, Sport


class CatalogFilterTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Экипировка', slug='ekipirovka')
        self.sport_box = Sport.objects.create(name='Бокс', slug='boks')

        self.product_box = Product.objects.create(
            category=self.category, name='Боксерские перчатки',
            slug='gloves', price=Decimal('5000.00'), stock=10
        )
        self.product_box.sports.add(self.sport_box)

        self.product_uni = Product.objects.create(
            category=self.category, name='Спортивная бутылка',
            slug='bottle', price=Decimal('1000.00'), stock=20
        )

    def test_6_filter_by_sport(self):
        response = self.client.get('/?sport=Бокс')

        self.assertContains(response, 'Боксерские перчатки')

        self.assertContains(response, 'Спортивная бутылка')

    def test_7_search_by_name(self):
        response = self.client.get('/?q=перчатки')

        self.assertContains(response, 'Боксерские перчатки')
        self.assertNotContains(response, 'Спортивная бутылка')