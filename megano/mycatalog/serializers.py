from typing import Any, Dict, List
from rest_framework import serializers
from .models import Categories, Product, Tag, Review


class CategoriesSerializer(serializers.ModelSerializer):

    """Сериалайзер для обработки данных о категориях"""

    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Categories
        fields = ('id', 'title', 'image', 'subcategories')

    def get_subcategories(self, instance: Categories) -> Dict[str, Any]:
        subcategories = Categories.objects.filter(parent_category=instance)
        serializer = CategoriesSerializer(subcategories, many=True)
        return serializer.data

    def get_image(self, instance: Categories) -> Dict[str, Any]:
        image_instance = instance.category_image.first()
        src = image_instance.image.url
        alt = image_instance.image.name
        return {"src": src, "alt": alt}


class ProductSerializer(serializers.ModelSerializer):

    """Сериалайзер для обработки данных о продуктах"""

    images = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "category", "price", "count", "date", "title",
                  "description", "freeDelivery", "images", "tags", "reviews", "rating")

    @staticmethod
    def get_reviews(instance: Product) -> int:
        return instance.review.all().count()

    @staticmethod
    def get_rating(instance: Product) -> float:
        return instance.rating

    @staticmethod
    def get_images(instance: Product) -> List[Dict[str, Any]]:
        image_instance = instance.images.all()
        images = []
        for inst in image_instance:
            src = inst.image.url
            alt = inst.image.name
            images.append({"src": src, "alt": alt})
        return images

    def to_representation(self, instance: Product) -> Dict[str, List[dict]]:
        data = super().to_representation(instance)
        tag_ids = data["tags"]
        data["tags"] = []
        queryset = Tag.objects.filter(id__in=tag_ids)
        for tag in queryset:
            data["tags"].append({"id": tag.id, "name": tag.name,})
        return data


class SaleProductSerializer(serializers.ModelSerializer):

    """Сериалайзер обрабатывающий данные о скидках """

    images = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ("id", "price", "title", "images",)

    def get_images(self, instance: Product) -> List[Dict[str, Any]]:
        image_instance = instance.images.all()
        images = []
        for inst in image_instance:
            src = inst.image.url
            alt = inst.image.name
            images.append({"src": src, "alt": alt})
        return images

    def to_representation(self, instance: Product) -> Dict[str, Any]:
        data = super().to_representation(instance)
        sale_info = instance.sale
        price = float(data["price"])
        data["salePrice"] = price - round(sale_info.discount * price / 100, 2)
        data["dateFrom"] = sale_info.date_from.strftime("%m-%d")
        data["dateTo"] = sale_info.date_to.strftime("%m-%d")
        return data


class ProductIDSerializer(serializers.ModelSerializer):

    """Сериалайзер обрабатывающий детальные данные о продуктах  """

    specifications = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("specifications", "reviews", "fullDescription",)

    @staticmethod
    def get_specifications(instance: Product) -> List[Dict[str, Any]]:
        specifications_inst = instance.specifications.all()
        specifications = []
        for sp in specifications_inst:
            name = sp.name
            value = sp.value
            specifications.append({"name": name, "value": value})
        return specifications

    @staticmethod
    def get_reviews(instance: Product) -> List[Dict[str, Any]]:
        reviews_inst = instance.review.all()
        reviews = []
        for review in reviews_inst:
            author = review.author.profile.fullName
            email = review.author.profile.email
            text = review.text
            rate = review.rate
            date = review.date
            reviews.append({
                "author": author,
                "email": email,
                "text": text,
                "rate": rate,
                "date": date
            })
        return reviews

    def to_representation(self, instance: Product) -> Dict[str, Any]:
        data = super().to_representation(instance)
        serializer = ProductSerializer(instance)
        product_data = serializer.data
        del product_data["reviews"]
        data.update(product_data)
        return data


class ReviewSerializer(serializers.ModelSerializer):

    """Сериалайзер обрабатывающий данные об отзывах """

    class Meta:
        model = Review
        fields = ['author', 'product', 'text', 'rate', 'date']


class TagsSerializer(serializers.ModelSerializer):

    """Сериалайзер обрабатывающий данные о тегах"""

    class Meta:
        model = Tag
        fields = ("id", "name")
