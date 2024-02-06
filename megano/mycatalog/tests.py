from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase
from django.http import QueryDict
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import authenticate
import json
from .models import Categories, CategoryImage, Review


class CategoriesViewTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        self.category = Categories.objects.create(
            title="test_title",
        )
        self.child_category = Categories.objects.create(
            title="child",
            parent_category=self.category,
        )
        self.category_image = CategoryImage.objects.create(
            image=self.image,
            category=self.category

        )
        self.category_image2 = CategoryImage.objects.create(
            image=self.image,
            category=self.child_category
        )

    def tearDown(self):
        Categories.objects.filter(title='child').delete()
        Categories.objects.filter(title='test_title').delete()

    def test_categories_get(self):
        url = reverse('mycatalog:categories')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CatalogViewTestCase(APITestCase):
    fixtures = [
        'categories.json',
        'category_images.json',
        'tags.json',
        'specifications.json',
        'products.json',
        'users',
        'reviews.json'
    ]
    def test_product_catalog(self):

        clean_query = {
            "name": "",
            "minPrice": 0,
            "maxPrice": 50000,
            "freeDelivery": 'false',
            "available": 'true'
        }
        query_dict = QueryDict(mutable=True)
        for key, value in clean_query.items():
            query_dict[f"filter[{key}]"] = value
        url = reverse('mycatalog:catalog')
        response = self.client.get(url, data=query_dict)
        expected_keys = ['items', 'currentPage', 'lastPage']
        self.assertEqual(set(response.json().keys()), set(expected_keys))
        self.assertEqual(response.status_code, 200)


class ProductsLimitedViewTestCase(APITestCase):
    fixtures = [
        'categories.json',
        'category_images.json',
        'tags.json',
        'specifications.json',
        'products.json',
        'users',
        'reviews.json'
    ]
    def test_product_limited(self):
        url = reverse('mycatalog:popular')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)


class SalesViewTestCase(APITestCase):
    fixtures = [
        'categories.json',
        'category_images.json',
        'tags.json',
        'specifications.json',
        'products.json',
        'users',
        'reviews.json'
    ]

    def test_sales(self):
        url = reverse('mycatalog:sales')
        data = {'currentPage': '2'}
        query_dict = QueryDict(mutable=True)
        query_dict.update(data)
        response = self.client.get(url, data=query_dict)
        self.assertEqual(response.status_code, 200)
        expected_keys = ['items', 'currentPage', 'lastPage']
        self.assertEqual(set(response.json().keys()), set(expected_keys))
        self.assertEqual(response.json().get('currentPage'), int(data.get('currentPage')))


class ProductsPopularTestCase(APITestCase):
    fixtures = [
        'categories.json',
        'category_images.json',
        'tags.json',
        'specifications.json',
        'products.json',
        'users',
        'reviews.json'
    ]
    def test_popular_products(self):
        url = reverse('mycatalog:popular')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)



class BannersTestCase(APITestCase):
    fixtures = [
        'categories.json',
        'category_images.json',
        'tags.json',
        'specifications.json',
        'products.json',
        'users',
        'reviews.json'
    ]
    def test_banners(self):
        url = reverse('mycatalog:banners')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)


class ProductViewTestCase(APITestCase):

    fixtures = [
        'categories.json',
        'category_images.json',
        'tags.json',
        'specifications.json',
        'products.json',
        'users',
        'reviews.json'
    ]

    def test_product(self):
        product_id = 1
        data = {"id": 1}
        url = reverse('mycatalog:product', args=[product_id])
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# class ReviewViewTestCase(APITestCase):
#     # при использовании данного теста необходимо
#     # закоментировать сигнал создания профиля
#     # в myauth.models "create_or_update_user_profile"
#     # не забудьте разкоментировать после использования теста
#     fixtures = [
#         'categories.json',
#         'category_images.json',
#         'tags.json',
#         'users',
#         'specifications.json',
#         'avatars.json',
#         'products.json',
#         'reviews.json',
#         'profiles.json',
#
#     ]
#
#     def setUp(self):
#         self.client = APIClient()
#         self.user = authenticate(username='bob', password='bob')
#         self.client.force_authenticate(user=self.user)
#
#     def test_review(self):
#
#         product_id = 6
#         data = {'author': 'bob', 'email': 'karen.g.tek@gmail.com', 'text': 'lklkl', 'rate': 5}
#         data_json = json.dumps(data)
#         url = reverse('mycatalog:reviews', args=[product_id])
#         response = self.client.post(url, data=data_json, content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         reviews_count = Review.objects.filter(author=self.user.pk, product=product_id).count()
#         self.assertEqual(reviews_count, 1, 'Expected one review object in the database.')



