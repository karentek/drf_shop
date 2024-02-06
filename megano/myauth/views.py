import json
from rest_framework import status
from django.core.cache import cache
from rest_framework import generics
from .models import Profile, Avatar
from rest_framework.views import APIView
from rest_framework.request import Request
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
from drf_spectacular.openapi import OpenApiTypes, OpenApiParameter
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import SignUpSerializer, ProfileGetPostSerializer, SignInSerializer, PasswordSerializer


@extend_schema(tags=["myauth APP"])
@extend_schema_view(
    post=extend_schema(
        summary="Метод для создания, авторизации и регистрации пользователя",
        description="Метод для создания, авторизации и регистрации пользователя",
        request=None,
        responses=None,
        parameters=[
            OpenApiParameter("name", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("username", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("password", OpenApiTypes.UUID, OpenApiParameter.QUERY),
        ],
    ),
)
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
                return Response({'message': serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["myauth APP"])
@extend_schema_view(
    post=extend_schema(
        summary="Метод для аутентикации  пользователя и входа на сайт",
        description="""Метод для аутентикации  пользователя и входа на сайт""",
        request=None,
        responses=None,
        parameters=[
            OpenApiParameter("username", OpenApiTypes.UUID, OpenApiParameter.QUERY),
            OpenApiParameter("password", OpenApiTypes.UUID, OpenApiParameter.QUERY),
        ],
    ),
)
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


@extend_schema(tags=["myauth APP"])
@extend_schema_view(
    post=extend_schema(
    summary="Метод для выхода с сайта",
    description="""Метод для выхода с сайта""",

    ),
)
class LogoutView(APIView):
    """
    Класс представления для выхода с сайта
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@extend_schema(tags=["myauth APP"])
@extend_schema_view(
    post=extend_schema(
        summary="Метод для обновления или создания дополнительной информации о пользователе",
        description="""Метод для обновления или создания дополнительной информации о пользователе""",
        responses=None
    ),
    get=extend_schema(
        summary="Метод для обновления или создания дополнительной информации о пользователе",
        description="""Метод для обновления или создания дополнительной информации о пользователе""",
        responses=None

    ),

)
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
            cache.set('profile_cache', profile, 20)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        profile_cache_name = 'profile_cache'
        profile_cache = cache.get(profile_cache_name)
        if profile_cache:
            profile = profile_cache
        else:
            profile = get_object_or_404(Profile, user=user)
            cache.set(profile_cache_name, profile, 20)
        serializer = ProfileGetPostSerializer(instance=profile)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["myauth APP"])
class PostPasswordView(APIView):
    """
    Класс представления для смены пароля пользователя
    """

    @extend_schema(
            summary="Метод для смены пароля пользователя",
            description="""Метод для смены пароля пользователя""",
            responses=None,
            request=PasswordSerializer,
    )
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


@extend_schema(tags=["myauth APP"])
@extend_schema_view(
    post=extend_schema(
        summary="Метод для сохранения и отображения  аватара пользователя.",
        description="""Метод для сохранения и отображения  аватара пользователя.""",
        responses=None,
        request=None,
    ),
)
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
        cache.set('profile_cache', profile, 20)
        response_data = {
            'src': avatar.image.url,
            'alt': 'Image alt string',
        }
        return Response(response_data, status=status.HTTP_201_CREATED)