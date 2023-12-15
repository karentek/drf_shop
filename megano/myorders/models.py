from django.db import models
from django.contrib.auth.models import User
from mycatalog.models import Product, Tag, Categories, Specification


class Order(models.Model):
    """
    Модель для заказов
    """
    createdAt = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    paymentType = models.CharField(max_length=10, null=True, blank=True)
    deliveryType = models.CharField(max_length=10, null=True, blank=True)
    totalCost = models.DecimalField(decimal_places=2, default=0, max_digits=10, null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    products = models.ManyToManyField(Product, related_name="orders")


class OrderItem(models.Model):
    """
    Модель для хранения данных о колличестве товара и ее цене.
    Данные сохраняются перед удалением из корзины с сессии
    """
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    count = models.IntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")


class Payment(models.Model):
    """
    Данные карты
    """
    order_rel = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    name = models.CharField(max_length=30)
    number = models.IntegerField()
    year = models.IntegerField()
    code = models.IntegerField()

