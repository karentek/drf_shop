from django.contrib import admin

from .models import OrderItem, Order, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'createdAt', 'user', 'paymentType', 'deliveryType', 'totalCost', 'status', 'city', 'address']
    search_fields = ['user__username', 'city', 'status']
    list_filter = ['createdAt', 'status']
    inlines = [OrderItemInline, PaymentInline]

    def total_cost(self, obj):
        return f"${obj.totalCost:.2f}"
    total_cost.short_description = 'Total Cost'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'price', 'count', 'product']
    search_fields = ['order__user__username', 'product__name']
    list_filter = ['order__createdAt']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_rel', 'name', 'number', 'year', 'code']
    search_fields = ['order_rel__user__username', 'name']
    list_filter = ['order_rel__createdAt']
    readonly_fields = ['order_rel']
