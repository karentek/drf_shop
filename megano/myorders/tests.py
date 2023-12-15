import json
from .models import Order
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class BayProductTestCase(APITestCase):

    fixtures = [
        'categories.json',
        'category_images.json',
        'tags.json',
        'specifications.json',
        'products.json',
        'users',
        'reviews.json'
    ]

    def tearDown(self):

        Order.objects.filter(user=self.user).delete()
        User.objects.filter(username='testuser').delete()

    def test_post_get_delete_basket(self):

        query = {
              "id": 1,
              "count": 1
        }
        url = reverse('myorders:basket')
        response = self.client.post(url, data=query)
        self.assertEqual(response.status_code, 200)
        self.assertIn('basket', self.client.session)
        self.assertIn('1', self.client.session['basket'])
        self.assertEqual(self.client.session['basket']['1'], 1)

        query = {
            "id": 1,
            "count": 3
        }
        response = self.client.post(url, data=query)
        self.assertEqual(response.status_code, 200)
        self.assertIn('basket', self.client.session)
        self.assertIn('1', self.client.session['basket'])
        self.assertEqual(self.client.session['basket']['1'], 2)

        query = {
            "id": 1,
            "count": 1
        }
        response = self.client.delete(url, data=query)
        self.assertEqual(response.status_code, 200)
        self.assertIn('basket', self.client.session)
        self.assertIn('1', self.client.session['basket'])
        self.assertEqual(self.client.session['basket']['1'], 1)

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user.profile.fullName = "Test FullName"
        self.user.profile.email = "email@email.com"
        self.user.profile.phone = "999999999"
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

        self.assertTrue(self.user.is_authenticated)
        url = reverse('myorders:orders')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['basket']['1'], 1)
        data = response.json()
        order_id = data["orderId"]
        url = reverse('myorders:orders-pk', args=[order_id])

        with open('mycatalog/fixtures/products.json', 'r') as file:
            products_data = json.load(file)

        products = [product for product in products_data if product["pk"] == 1]
        products = products[0]["fields"]
        products["id"] = 1
        products["count"] = 1
        order = Order.objects.get(id=order_id)

        order_data = {
            'orderId': order_id,
            'createdAt': order.createdAt,
            'fullName': self.user.profile.fullName,
            'phone': self.user.profile.phone,
            'email': self.user.profile.email,
            'deliveryType': 'express',
            'city': 'Москва',
            'address': 'Народная\n5',
            'paymentType': 'someone',
            'status': 'in_process',
            'totalCost': '1000.00',
            'products': products
        }

        response = self.client.post(url, data=order_data, format='json')
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertTrue(order.city == 'Москва')
        self.assertTrue(order.status == 'accepted')

        url = reverse('myorders:payment', args=[order_id])

        data = {
            "number": "9999999999999999",
            "name": "Annoying Orange",
            "month": "02",
            "year": "2025",
            "code": "123"
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertTrue(order.payment.name == "Annoying Orange")
        self.assertTrue(order.status == "payed")