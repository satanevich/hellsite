from frontend.models import Products, Tags, Category, Reviews, Profile, Order, Delivery
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = [
            'id',
            'title',
            'images',
            'description',
            'price',
            'count',
            'freeDelivery',
            'category',
            'tags',
            'available',
            'rating',
        ]


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = [
            'name'
        ]


class CatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'name',
            'parent',
            'icon',
            'is_active',
        ]


# class ImagesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Images
#         fields = [
#             'image',
#         ]

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = [
            'author',
            'email',
            'rating',
            'product',
            'name',
            'date',
        ]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'avatar',
            'phone',
            'user_id',
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'created_at',
            'full_name',
            'email',
            'phone',
            'delivery_type',
            'payment_type',
            'total_cost',
            'status',
            'city',
            'address',
            'products',
        ]


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = [
            'name',
            'price',
        ]



