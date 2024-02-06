import random
from django.core.cache import cache
from typing import Any, List, Dict
from drf_spectacular.openapi import OpenApiTypes, OpenApiParameter
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from .tasks import count_rating, test_task
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import DecimalField, IntegerField
from rest_framework.permissions import IsAuthenticated
from .models import Categories, Product, Tag
from .services import CatalogPaginator, DataFilter
from .for_swagger import Product_ID_sw, CatalogSw, QuerySerializerFilter, ProductSw, Sales_Sw
from .serializers import (
    CategoriesSerializer,
    ProductSerializer,
    SaleProductSerializer,
    ProductIDSerializer,
    ReviewSerializer,
    TagsSerializer,
)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения категорий",
        description="""Метод для отображения тэгов""",
        responses={
                status.HTTP_200_OK: CategoriesSerializer,
            },
        ),
)
class CategoriesView(APIView):

    """Вью для отображения категорий"""

    def get(self, request):
        categories_cache_name = 'categories_cache'
        categories_cache = cache.get(categories_cache_name)
        if categories_cache:
            categories = categories_cache
        else:
            categories = Categories.objects.filter(parent_category=None)
            cache.set(categories_cache_name, categories, 20)
        serializer = CategoriesSerializer(instance=categories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения каталога и фильтрации продуктов",
        description="""Метод для отображения каталога и фильтрации продуктов""",
        responses={
                status.HTTP_200_OK: CatalogSw,
            },
        parameters=[
            OpenApiParameter("filter", QuerySerializerFilter),
            OpenApiParameter("currentPage", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("category", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("sort", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("sortType", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("tags", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("limit", OpenApiTypes.UUID, OpenApiParameter.QUERY),

        ],

    ),
)
class CatalogView(APIView):

    """Вью для отображения каталога и фильтрации продуктов"""

    def get(self, request: Request) -> Response:
        catalog_cache_name = 'catalog_cache'
        catalog_cache = cache.get(catalog_cache_name)
        if catalog_cache:
            queryset = catalog_cache
        else:
            queryset = Product.objects.all()
            cache.set(catalog_cache_name, queryset, 20)
        data_filter_object = DataFilter(self.request.query_params)
        filtered_products = data_filter_object.apply_filters_to_products(queryset)
        query = data_filter_object.filtered_dict
        paginator = CatalogPaginator()
        result_page = paginator.paginate_queryset(filtered_products, request, query)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения популярных продуктов",
        description="""Метод для отображения популярных продуктов, 
                       выводятся 4 самых рейтинговых продукта""",
        responses={
                status.HTTP_200_OK: ProductSw(many=True),
            },
        ),
)
class ProductsPopularView(APIView):

    """Вью для отображения популярных продуктов"""

    def get(self, request):
        products_cache_name = 'catalog_cache'
        product_popular_cache = cache.get(products_cache_name)
        if product_popular_cache:
            product = product_popular_cache
        else:
            product = Product.objects.all()
            cache.set(products_cache_name, product, 20)
        product = product.annotate(
            rating_coalesced=Coalesce('rating', -1, output_field=DecimalField())
        ).order_by('-rating_coalesced')
        product = product[:4]
        serializer = ProductSerializer(instance=product, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения лимитированных продуктов",
        description="""Метод для отображения лимитированныхх продуктов, 
                       выводится продукты с наименьшим колличеством в остатках""",
        responses={
                status.HTTP_200_OK: ProductSw(many=True),
            },
        ),
)
class ProductsLimitedView(APIView):

    """Вью для отображения лимитированных продуктов"""

    def get(self, request) -> Response:
        products_limited_name = 'product_limited_cache'
        product_limited_cache = cache.get(products_limited_name)
        if product_limited_cache:
            product = product_limited_cache
        else:
            product = Product.objects.exclude(count__isnull=True).exclude(count=0)
            cache.set(products_limited_name, product, 20)
        product = product.annotate(
            product_count_coalesced=Coalesce('count', -1, output_field=IntegerField())
        ).order_by('product_count_coalesced')
        product = product[:4]
        serializer = ProductSerializer(instance=product, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения скидок на продукты",
        description="""Метод для отображения скидок на продукты, скидка указывается в админке
                        в нижней части продукта""",
        responses={
                status.HTTP_200_OK: Sales_Sw,
            },
        ),
)
class SalesView(APIView):

    """Вью для отображения скидок на продукты"""

    def get(self, request: Request) -> Response:
        product = Product.objects.exclude(sale__isnull=True)
        paginator = CatalogPaginator()
        current_page = {
            "currentPage": int(self.request.query_params.get("currentPage"))
        }
        result_page = paginator.paginate_queryset(product, request, current_page)
        serializer = SaleProductSerializer(instance=result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения банеров продуктов",
        description="""Метод для отображения банеров продуктов, выводит список
                        из тех продуктов которые есть в наличии и присутствуют в остатках, выводится
                        результат из 4-х таких случайных продуктов"""
        ,
        responses={
                status.HTTP_200_OK: ProductSw(many=True),
            },
        ),
)
class BannersView(APIView):

    """Вью для отображения банеров продуктов"""

    def get(self, request: Request) -> Response:
        all_ids = Product.objects.filter(count__gt=0).values_list('pk', flat=True)
        random_ids = random.sample(list(all_ids), 4)
        random_inst_cach_name = 'random_inst_cach_name'
        random_inst_cach = cache.get(random_inst_cach_name)
        if random_inst_cach:
            random_instances = random_inst_cach
        else:
            random_instances = Product.objects.filter(pk__in=random_ids)
            cache.set(random_inst_cach_name, random_instances, 3)
        serializer = ProductSerializer(instance=random_instances, many=True)
        serialized_data: List[Dict[str, Any]] = serializer.data
        return Response(data=serialized_data, status=status.HTTP_200_OK)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения детальной информации о продуктах",
        description="""Метод для отображения детальной информации о продуктах"""
        ,
        responses={
                status.HTTP_200_OK: Product_ID_sw,
            },
        ),
)
class ProductView(APIView):

    """Вью для отображения детальной информации о продуктах"""

    def get(self, request: Request, **kwargs: Any) -> Response:
        product_cache_id_name = 'product_cache_id'
        product_cache_id = cache.get(product_cache_id_name)
        if product_cache_id:
            product = product_cache_id
        else:
            product = Product.objects.get(id=self.kwargs.get("id"))
            cache.set(product_cache_id_name, product, 3)
        serializer = ProductIDSerializer(instance=product)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    post=extend_schema(
        summary="Метод для написания отзыва",
        description="""Метод для написания отзыва.
                       Только авторизованный пользователь может оставить отзыв,
                       также проверяется правильность ввода почты и имени пользователя""",
        request=ReviewSerializer,
        responses={
                status.HTTP_201_CREATED: ReviewSerializer,
            },
        ),
)
class ReviewView(APIView):

    """Вью для написания отзыва.
    Только авторизованный пользователь может оставить отзыв,
    также проверяется правильность ввода почты и имени пользователя"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        data = request.data
        user = request.user
        author = data.get('author')
        email = data.get('email')
        if user.username != author:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.profile.email != email:
            return Response({'error': 'Email does not match.'}, status=status.HTTP_400_BAD_REQUEST)
        data['author'] = user.pk
        data['product'] = kwargs.get("id")
        product_id = data['product']
        serializer = ReviewSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            count_rating.delay(product_id)
            # test_task.delay(product_id)
            return Response({'message': 'Review posted successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["mycatalog APP"])
@extend_schema_view(
    get=extend_schema(
        summary="Метод для отображения тэгов",
        description="""Метод для отображения тэгов""",
        responses={
                status.HTTP_200_OK: TagsSerializer,
            },
        ),
)
class TagsView(APIView):

    """Вью для отображения тэгов"""

    def get(self, request: Request, **kwargs: Any) -> Response:
        tags_cache_name = 'tags_cache'
        tags_cache = cache.get(tags_cache_name)
        if tags_cache:
            tags = tags_cache
        else:
            tags = Tag.objects.all()
            cache.set(tags_cache_name, tags, 3)
        serializer = TagsSerializer(instance=tags, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)