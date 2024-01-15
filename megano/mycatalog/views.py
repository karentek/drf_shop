import random
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models.functions import Coalesce
from django.db.models import DecimalField, IntegerField
from rest_framework.permissions import IsAuthenticated
from .models import Categories, Product, Tag
from .services import DataFilter, CatalogPaginator
from .serializers import (
    CategoriesSerializer,
    ProductSerializer,
    SaleProductSerializer,
    ProductIDSerializer,
    ReviewSerializer,
    TagsSerializer
)


class CategoriesView(APIView):

    """Вью для отображения категорий"""

    def get(self, request):
        categories = Categories.objects.filter(parent_category=None)
        serializer = CategoriesSerializer(instance=categories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CatalogView(APIView):

    """Вью для отображения каталога и фильтрации продуктов"""

    def get(self, request):
        queryset = Product.objects.all()
        data_filter_object = DataFilter(self.request.query_params)
        filtered_products = data_filter_object.apply_filters_to_products(queryset)
        query = data_filter_object.filtered_dict
        paginator = CatalogPaginator()
        result_page = paginator.paginate_queryset(filtered_products, request, query)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductsPopularView(APIView):

    """Вью для отображения популярных продуктов"""

    def get(self, request):
        product = Product.objects.all()
        product = product.annotate(
            rating_coalesced=Coalesce('rating', -1, output_field=DecimalField())
        ).order_by('-rating_coalesced')
        product = product[:4]
        serializer = ProductSerializer(instance=product, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductsLimitedView(APIView):

    """Вью для отображения лимитированных продуктов"""

    def get(self, request):
        product = Product.objects.exclude(count__isnull=True).exclude(count=0)
        product = product.annotate(
            product_count_coalesced=Coalesce('count', -1, output_field=IntegerField())
        ).order_by('product_count_coalesced')
        product = product[:4]
        serializer = ProductSerializer(instance=product, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class SalesView(APIView):

    """Вью для отображения скидок на продукты"""

    def get(self, request):
        product = Product.objects.exclude(sale__isnull=True)
        paginator = CatalogPaginator()
        current_page = {
            "currentPage": int(self.request.query_params.get("currentPage"))
        }
        result_page = paginator.paginate_queryset(product, request, current_page)
        serializer = SaleProductSerializer(instance=result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class BannersView(APIView):

    """Вью для отображения банеров продуктов"""

    def get(self, request):
        all_ids = Product.objects.filter(count__gt=0).values_list('pk', flat=True)
        random_ids = random.sample(list(all_ids), 4)
        random_instances = Product.objects.filter(pk__in=random_ids)
        serializer = ProductSerializer(instance=random_instances, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductView(APIView):

    """Вью для отображения детальной информации о продуктах"""

    def get(self, request, **kwargs):
        product = Product.objects.get(id=self.kwargs.get("id"))
        serializer = ProductIDSerializer(instance=product)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ReviewView(APIView):

    """Вью для написания отзыва.
    Только авторизованный пользователь может оставить отзыв,
    также проверяется правильность ввода почты и имени пользователя"""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
        serializer = ReviewSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Review posted successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagsView(APIView):

    """Вью для отображения тэгов"""

    def get(self, request, **kwargs):
        tags = Tag.objects.all()
        serializer = TagsSerializer(instance=tags, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)