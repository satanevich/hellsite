from django.contrib.auth import get_user_model
from django.db import models
from datetime import datetime

from RealShit.settings import BASE_DIR

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='category_icons', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# class Images(models.Model):
#     image = models.ImageField(default="images/сумки.jpg", upload_to=f'{BASE_DIR} / images/', null=True, blank=True, verbose_name='Изображение товара')
#
#     def __str__(self):
#         return self.image


class Products(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name='Название товара')
    images = models.ImageField(default="images/bigGoods.png", upload_to=f'media/images/', null=True, blank=True,
                              verbose_name='Изображение товара')
    # images = models.ManyToManyField(Images, verbose_name='Изображение товара')
    description = models.CharField(max_length=200, verbose_name='Описание товара')
    price = models.FloatField(verbose_name='Цена товара')
    count = models.IntegerField(verbose_name='Количество товара')
    freeDelivery = models.BooleanField(verbose_name='Бесплатная доставка')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags)
    available = models.BooleanField(verbose_name='Доступный', default=True)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Reviews(models.Model):
    #user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank = True, null = True)
    author = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, default='')
    rating = models.IntegerField(default=0)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, default='1')
    name = models.CharField(max_length=255,default='')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    avatar = models.ImageField(upload_to='avatarts', verbose_name='Аватарка')
    phone = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    full_name = models.CharField(max_length=100, default='')
    email = models.EmailField(default='')
    phone = models.CharField(max_length=20, default='')
    delivery_type = models.CharField(max_length=20, default='free')
    payment_type = models.CharField(max_length=20, default='online')
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='accepted')
    city = models.CharField(max_length=50, default='Moscow')
    address = models.CharField(max_length=100, default='red square 1')
    products = models.ManyToManyField(Products, default=None)

    def __str__(self):
        return f'Order #{self.id}'

class Delivery(models.Model):
    name = models.CharField(verbose_name='Доставка', max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name
