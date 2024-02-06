from django.db import models
from django.contrib.auth.models import User


class Categories(models.Model):

    """Модель категории"""

    title = models.CharField(max_length=255)
    parent_category = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.title!r}"


def category_images_directory_path(instance: "CategoryImage", filename: str) -> str:

    """функция-помощник для обработки пути картинки категории"""

    return "category_images/category_{title}/{filename}".format(
        title=instance.category.title,
        filename=filename,
    )


class CategoryImage(models.Model):

    """Модель картинки категорий"""

    image = models.ImageField(
        null=True, blank=True, upload_to=category_images_directory_path
    )
    category = models.ForeignKey(
        Categories, on_delete=models.CASCADE, null=True, blank=True, related_name="category_image"
    )


class Tag(models.Model):

    """Модель для тегов"""

    name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.name!r}"


class Specification(models.Model):

    """Модель для спецификаций"""

    name = models.CharField(max_length=50, null=True, blank=True)
    value = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name!r}: {self.value}"


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:

    """функция-помощник для обработки пути картинки товара"""

    return "products_images/product_{title}/{filename}".format(
        title=instance.images_product.title,
        filename=filename,
    )


class ProductImage(models.Model):

    """Модель картинки товаров"""

    image = models.ImageField(
        null=True, blank=True, upload_to=product_images_directory_path
    )
    images_product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images"
    )


class Product(models.Model):

    """Модель товаров"""

    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    fullDescription = models.TextField(max_length=600, null=True, blank=True, db_index=True)
    description = models.TextField(max_length=300, null=True, blank=True, db_index=True)
    freeDelivery = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name="product")
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    specifications = models.ManyToManyField(Specification, related_name="product")
    rating = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.title!r}"


class Review(models.Model):

    """Модель отзывов"""

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="review")
    text = models.TextField(max_length=500, null=False, blank=True, db_index=True)
    rate = models.SmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)


class SaleDate(models.Model):

    """Модель скидок и распродаж"""

    date_from = models.DateTimeField(blank=True, null=True)
    date_to = models.DateTimeField(blank=True, null=True)
    discount = models.SmallIntegerField(default=0, blank=True, null=True)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="sale")
