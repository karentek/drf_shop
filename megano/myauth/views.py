import json
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.request import Request
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
from .serializers import SignUpSerializer, ProfileGetPostSerializer
from .models import Profile, Avatar


class SignUpView(generics.CreateAPIView):
    """
    Класс представления для создания, авторизации и регистрации пользователя
    """
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        if request.method == 'POST':
            serializer = SignUpSerializer(data=request.data)
            if serializer.is_valid():
                password = serializer.validated_data['password']
                username = serializer.validated_data['username']
                first_name = serializer.validated_data['first_name']
                user = User(username=username, first_name=first_name)
                user.set_password(password)
                user.save()
                authenticated_user = authenticate(request, password=password, username=username)
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'message': 'Not serialized or not valid'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignInView(APIView):
    """
    Класс представления для аутентикации  пользователя и входа на сайт
    """
    def post(self, request: Request) -> Response:
        cleaned_data = json.loads(list(request.POST.keys())[0])
        password = cleaned_data['password']
        username = cleaned_data['username']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'message': 'Login successful'},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {'message': 'Log in error'},
                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'User is not None'},
                            status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    """
    Класс представления для выхода с сайта
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    """
    Класс представления для обновления или создания дополнительной информации о пользователе
    """

    def post(self, request: Request) -> Response:
        data = request.data
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        serializer = ProfileGetPostSerializer(data=data, instance=profile)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        serializer = ProfileGetPostSerializer(instance=profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostPasswordView(APIView):
    """
    Класс представления для смены пароля пользователя
    """
    def post(self, request: Request) -> Response:
        user = self.request.user
        data = self.request.data
        current_password = data['currentPassword']
        new_password_input = data['newPassword']
        if check_password(current_password, user.password):
            user.set_password(new_password_input)
            user.save()
            authenticated_user = authenticate(request, username=user.username, password=new_password_input)
            login(request, authenticated_user)
            return Response({'message': 'New password successfully changed'}, status=status.HTTP_200_OK)
        else:
            return Response({'Old password is incorrect.'}, status=status.HTTP_200_OK)


class PostAvatarView(APIView):
    """
    Класс представления для сохранения и отображения  аватара пользователя.
    """

    def post(self, *args, **kwargs):
        file = self.request.FILES["avatar"]
        user = self.request.user
        profile = Profile.objects.get(user=user)
        avatar = Avatar(image=file)
        profile.avatar_image = avatar
        avatar.profile_rel = profile
        avatar.save()
        profile.save()
        response_data = {
            'src': avatar.image.url,
            'alt': 'Image alt string',
        }
        return Response(response_data, status=status.HTTP_201_CREATED)