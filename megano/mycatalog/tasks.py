from celery import shared_task
from celery_singleton import Singleton
from django.db.models import F
import celery
from .models import Product, Review
from django.db.models import DecimalField, Count, QuerySet
from django.db.models.functions import Coalesce
from django.http import QueryDict


@shared_task()
def count_rating(product_id):
    instance = Product.objects.get(id=product_id)
    reviews_instances = instance.review.all()
    count = reviews_instances.count()
    rate_summ = 0
    if count > 0:
        for review in reviews_instances:
            rate_summ += review.rate
        result = round(rate_summ / count, 2)
        instance.rating = result
        instance.save()
    elif count == 0:
        instance.rating = rate_summ
        instance.save()


















