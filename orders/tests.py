from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from users.models import CustomUser
from catalog.models import Category, Product
from cart.cart import Cart
from orders.models import Order, OrderItem


class SportShopBusinessLogicTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='password123',
            email='test@mail.ru', phone='+79991234567'
        )

        self.category = Category.objects.create(name='Тренажеры', slug='trenazhery')

        self.product = Product.objects.create(
            category=self.category,
            name='Беговая дорожка',
            slug='begovaya-dorozhka',
            price=Decimal('50000.00'),
            stock=5
        )

        self.factory = RequestFactory()

    def test_1_product_stock_and_price(self):
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(self.product.price, Decimal('50000.00'))
        self.assertTrue(self.product.is_available)

    def test_2_cart_calculation(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        cart = Cart(request)
        cart.add(self.product, quantity=2)

        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_total_price(), Decimal('100000.00'))

    def test_3_order_creation_and_stock_deduction(self):
        order = Order.objects.create(
            user=self.user,
            first_name='Иван',
            last_name='Иванов',
            phone='+79991234567',
            email='test@mail.ru',
            address='г. Москва, ул. Бауманская',
            total_cost=Decimal('50000.00')
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=1
        )

        self.product.stock -= 1
        self.product.save()

        self.product.refresh_from_db()
        self.assertEqual(order.status, 'CREATED')
        self.assertEqual(self.product.stock, 4)

from django.test import TestCase
from users.forms import CustomUserCreationForm


class UserValidationTests(TestCase):
    def test_4_invalid_phone_rejected(self):
        """ТЕСТ 4: (Негативный) Попытка регистрации с коротким номером телефона"""
        form_data = {
            'username': 'testuser2',
            'first_name': 'Петр',
            'last_name': 'Петров',
            'email': 'petr@mail.ru',
            'phone': '123'  # Намеренно неверный телефон (п. 4.2.1 ТЗ)
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())  # Форма должна быть невалидной
        self.assertIn('phone', form.errors) # Ошибка должна быть именно в поле phone

    def test_5_invalid_email_rejected(self):
        """ТЕСТ 5: (Негативный) Попытка регистрации с неверным email"""
        form_data = {
            'username': 'testuser3',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'bademail',  # Отсутствует @
            'phone': '+79991234567'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)