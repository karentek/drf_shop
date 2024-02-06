import math
from typing import List, Dict, Any, Union
from rest_framework.request import Request
from .models import Product
from django.db.models import DecimalField, Count, QuerySet
from django.db.models.functions import Coalesce
from django.http import QueryDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CatalogPaginator(PageNumberPagination):
    """Класс пагинации"""
    page_size = 2

    def __init__(self):
        self.current_page = None
        self.summ_pages = None

    def get_paginated_response(self, data: List[Dict[str, Any]]) -> Response:
        return Response(
            {
                "items": data,
                "currentPage": self.current_page,
                "lastPage": self.summ_pages
            }
        )

    def paginate_queryset(self, queryset: List[Any], request: Request, query, view=None) -> Union[List[Any], Response, None]:
        self.current_page = query.get('currentPage', 1)
        self.summ_pages = math.ceil(queryset.count() / self.page_size)
        start_index = (self.current_page - 1) * self.page_size
        end_index = start_index + self.page_size
        return queryset[start_index:end_index]


class DataFilter:

    """Кастомный класс для фильтрации данных"""

    def __init__(self, query_dict: QueryDict):
        self.filtered_dict = self.query_filter(query_dict)
        self.limit = self.filtered_dict.get('limit', None)
        self.current_page = self.filtered_dict.get('currentPage', None)

    def query_filter(self, query_dict: QueryDict) -> Dict[str, Any]:

        """"метод предназначен для очистки словаря параметров запроса
        для удобства последующей обработки этого словаря"""

        filtered_dict = {}
        for key in query_dict.keys():
            values = query_dict.getlist(key)
            converted_values = [int(val) if val.isdigit() else val for val in values]
            if len(converted_values) > 1:
                filtered_dict[key] = converted_values
            else:
                filtered_dict[key] = converted_values[0]
        return filtered_dict

    def apply_filters_to_products(self, filtered_products: QuerySet[Product]) -> QuerySet[Product]:

        """метод для фильтрации и создания набора продуктов по заданным параметрам"""

        filter_criteria = self.filtered_dict
        category = filter_criteria.get('category')
        name = filter_criteria.get('filter[name]')
        min_price = filter_criteria.get('filter[minPrice]')
        max_price = filter_criteria.get('filter[maxPrice]')
        free_delivery = filter_criteria.get('filter[freeDelivery]')
        available = filter_criteria.get('filter[available]')
        sort = filter_criteria.get('sort')
        sort_type = filter_criteria.get('sortType')
        tags = filter_criteria.get('tags[]')
        print(max_price, min_price, "max" * 10)
        if category:
            filtered_products = filtered_products.filter(category=category)
        if tags and type(tags) == list:
            filtered_products = filtered_products.filter(tags__id__in=tags)
        elif type(tags) == int:
            filtered_products = filtered_products.filter(tags=tags)
        if name:
            filtered_products = filtered_products.filter(title__icontains=name)
        if min_price and max_price:
            filtered_products = filtered_products.filter(price__gte=min_price, price__lte=max_price)
        if free_delivery in ['true']:
            filtered_products = filtered_products.filter(freeDelivery=(free_delivery == 'true'))
        if available == 'true':
            filtered_products = filtered_products.filter(count__gt=0)
        if sort == 'price':
            sort_order = '-price' if sort_type == 'dec' else 'price'
            filtered_products = filtered_products.order_by(sort_order)
        elif sort == 'rating':
            sort_order = '-rating' if sort_type == 'dec' else 'rating'
            filtered_products = filtered_products.order_by(sort_order)
        elif sort == 'reviews':
            sort_order = '-total_reviews' if sort_type == 'dec' else 'total_reviews'
            filtered_products = filtered_products.annotate(
                total_reviews=Count('review')
            ).order_by(sort_order)
        elif sort == 'date':
            sort_order = '-date' if sort_type == 'dec' else 'date'
            filtered_products = filtered_products.order_by(sort_order)
        return filtered_products
