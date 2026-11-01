from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название категории")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-идентификатор (slug)")
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name="Родительская категория"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_list_by_category', args=[self.slug])


class Sport(models.Model):
    name = models.CharField(max_length=100, verbose_name="Вид спорта")
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Вид спорта"
        verbose_name_plural = "Виды спорта"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=250, verbose_name="Наименование товара")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="URL-идентификатор (slug)")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Изображение")
    description = models.TextField(blank=True, verbose_name="Описание")
    specifications = models.TextField(blank=True, verbose_name="Технические характеристики")

    sports = models.ManyToManyField(Sport, blank=True, related_name='products', verbose_name="Виды спорта",
                                    help_text="Оставьте пустым, если товар универсальный")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена (руб.)")
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток на складе")
    is_available = models.BooleanField(default=True, verbose_name="Доступен для заказа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.id, self.slug])