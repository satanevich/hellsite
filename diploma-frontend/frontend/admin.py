from django.contrib import admin
from .models import Category, Products, Images, Tags, Reviews, Profile, Order, Delivery

admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Images)
admin.site.register(Tags)
admin.site.register(Reviews)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(Delivery)