from rest_framework import serializers
from mycatalog.models import Categories, Product, Tag, Review
from mycatalog.serializers import ProductSerializer
from .models import Order, OrderItem, Payment
from .services import aply_count_for_product


class OrderSerializer(serializers.ModelSerializer):

    """
    Сериалайзер для обработки данных заказов, создает инстанс заказа
    """

    orderId = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Order
        fields = ("orderId",)

    def create(self, validated_data):

        """
        кастомное создание инстанса заказа в котором сохраняются необходимые поля
        привязывается к товарам, к пользователю, подсчитывается сумма, и присваивается статус
        """
        print()
        print("start OrdersView POST serializer")
        print()
        request = self.context.get("request")
        user = request.user
        product_data = request.data
        total_cost = sum(item['count'] * float(item['price']) for item in product_data)
        validated_data['totalCost'] = round(total_cost, 2)
        validated_data['user'] = user
        validated_data['status'] = "in_process"
        instance = super().create(validated_data)
        product_ids = [int(item.get("id", 0)) for item in product_data]
        products = Product.objects.filter(id__in=product_ids)
        instance.products.set(products)
        return instance


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Сериалайзер обработки заказов
    """
    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )

    def get_fullName(self, instance):
        return instance.user.profile.fullName

    def get_email(self, instance):
        return instance.user.profile.email

    def get_phone(self, instance):
        return instance.user.profile.phone

    def get_products(self, instance):
        items = self.context.get("basket")
        items = {k: int(v) for k, v in items.items() if v != 0}
        products = instance.products.all()
        product_serializer = ProductSerializer(products, many=True)
        result = aply_count_for_product(product_serializer.data, items)
        return result


class OrderAcceptedSerializer(serializers.ModelSerializer):

    """Сериалайзер для добавления дополнительных данных о заказе"""

    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "user",
            "order_items",
        )

    def update(self, instance, validated_data):
        print("IT IS validated_data" * 3, validated_data)
        order_items_data = self.context.get("products")
        print("IT IS order_items_data" * 3, order_items_data)
        instance.deliveryType = validated_data.get('deliveryType', instance.deliveryType)
        instance.paymentType = validated_data.get('paymentType', instance.paymentType)
        instance.status = "accepted"  # You may override the status here if needed
        instance.city = validated_data.get('city', instance.city)
        instance.address = validated_data.get('address', instance.address)
        order_items_list = []
        for item_data in order_items_data:
            product_id = int(item_data["id"])
            count = int(item_data["count"])
            price = float(item_data["price"])
            product_instance = Product.objects.get(id=product_id)
            product_instance.count -= count
            product_instance.save()
            order_item = OrderItem.objects.create(order=instance, product=product_instance, count=count, price=price)
            order_items_list.append(order_item)
        instance.order_items.set(order_items_list)
        instance.save()
        return instance


class PaymentSerializer(serializers.ModelSerializer):

    """Сериалайзер для обработки данных пластиковой карты"""

    class Meta:
        model = Payment
        fields = '__all__'


class OrdersGetSerializer(serializers.ModelSerializer):

    """Сериалайзе для вывода данных о заказе"""

    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    products = ProductSerializer(many=True)
    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )

    def get_fullName(self, instance: Order):
        print(instance,  type(instance))
        return instance.user.profile.fullName

    def get_email(self, instance):
        return instance.user.profile.email

    def get_phone(self, instance):
        return instance.user.profile.phone

