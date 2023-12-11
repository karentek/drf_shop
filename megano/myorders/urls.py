from django.urls import path

from .views import (
    BasketView,
    OrdersView,
    OrdersDetailView,
    PaymentView,

)

app_name = "myorders"

urlpatterns = [
    path("basket", BasketView.as_view(), name='basket'),
    path("orders", OrdersView.as_view(), name='orders'),
    path("order/<int:pk>", OrdersDetailView.as_view(), name='orders'),
    path("payment/<int:pk>", PaymentView.as_view(), name='payment'),

]