from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from django.http import QueryDict
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
import json
from .models import Profile


class SignUpViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        User.objects.filter(username='john_doe').delete()

    def test_successful_signup(self):
        data = {
            "name": "John",
            "username": "john_doe",
            "password": "secure_password",
        }
        # преобразуем data обратно в тот формат который приходит из фронта
        json_data = json.dumps(data)
        query_dict = QueryDict(json_data)
        response = self.client.post(reverse('myauth:sign-up'), query_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username='john_doe').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)



class SignInViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='john_doe', password='secure_password')

    def tearDown(self):
        User.objects.filter(username='john_doe').delete()

    def test_successful_signin(self):
        data = {
            "username": "john_doe",
            "password": "secure_password",
        }
        json_data = json.dumps(data)
        query_dict = QueryDict(json_data)
        response = self.client.post(reverse('myauth:sign-in'), query_dict)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_unsuccessful_signin(self):
        data = {
            "username": "john_doe",
            "password": "wrong_password",
        }
        json_data = json.dumps(data)
        query_dict = QueryDict(json_data)
        response = self.client.post(reverse('myauth:sign-in'), query_dict)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ProfileUpdateViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        User.objects.filter(username='testuser').delete()

    def test_profile_update(self):
        data = {
            'fullName': 'testuser',
            'avatar': None,
            'phone': '89030203959',
            'email': 'testuser@gmail.com',
        }
        url = reverse('myauth:profile')
        response = self.client.post(url, data, format='json')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_authenticated)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.profile.fullName, 'testuser')
        self.assertEqual(self.user.profile.phone, '89030203959')
        self.assertEqual(self.user.profile.email, 'testuser@gmail.com')

    def test_profile_get(self):
        url = reverse('myauth:profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fullName'], self.user.profile.fullName)

class PostPasswordViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        User.objects.filter(username='testuser').delete()


    def test_password_update(self):
        data = {
                "currentPassword": "testpassword",
                "newPassword": "newPass321"
        }
        url = reverse('myauth:post-password')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newPass321"))


class PostAvatarViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        User.objects.filter(username='testuser').delete()

    def test_post_avatar(self):
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        data = {'avatar': image}
        url = reverse('myauth:post-avatar')
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertTrue(Profile.objects.filter(user=self.user).exists())




