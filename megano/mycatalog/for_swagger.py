from typing import Any, Dict, List
from rest_framework import serializers
from .models import Categories, Product, Tag, Review


class ImageSw(serializers.Serializer):
    src = serializers.CharField()
    alt = serializers.CharField()

class TagSw(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class BusketSw(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()

class CatalogSerializerSwagger2(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    image = ImageSw()


class CatalogSerializerSwagger(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    image = ImageSw()
    subcategories = CatalogSerializerSwagger2()


class ProductSw(serializers.Serializer):
    id = serializers.IntegerField()
    category = serializers.CharField()
    price = serializers.IntegerField()
    count = serializers.IntegerField()
    date = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    freeDelivery = serializers.CharField()
    images = ImageSw(many=True)

    tags = TagSw(many=True)
    reviews = serializers.IntegerField()
    rating = serializers.IntegerField()


class CatalogSw(serializers.Serializer):
    items = ProductSw(many=True)
    currentPage = serializers.IntegerField()
    lastPage = serializers.IntegerField()


class QuerySerializerFilter(serializers.Serializer):
    name = serializers.IntegerField()
    minPrice = serializers.IntegerField()
    maxPrice = serializers.IntegerField()
    freeDelivery = serializers.BooleanField()
    avalible = serializers.BooleanField()


class SalesSw(serializers.Serializer):
    id = serializers.IntegerField()
    price = serializers.IntegerField()
    title = serializers.CharField()
    images = ImageSw(many=True)

    salePrice = serializers.IntegerField()
    dateFrom = serializers.IntegerField()
    dateTo = serializers.DateTimeField()


class Sales_Sw(serializers.Serializer):
    items = SalesSw(many=True)
    currentPage = serializers.IntegerField()
    lastPage = serializers.IntegerField()


class Reviews_sw(serializers.Serializer):
    author = serializers.CharField()
    email = serializers.CharField()
    text = serializers.CharField()
    rate = serializers.IntegerField()
    date = serializers.DateTimeField()


class Specifications_sw(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class Product_ID_sw(ProductSw):
    reviews = Reviews_sw(many=True)
    specifications = Specifications_sw(many=True)


class Order_sw(serializers.Serializer):
    createdAt = serializers.DateTimeField()
    user = serializers.CharField()
    paymentType = serializers.CharField()
    deliveryType = serializers.CharField()
    totalCost = serializers.CharField()
    status = serializers.CharField()
    city = serializers.CharField()
    address = serializers.CharField()
    products = ProductSw(many=True)