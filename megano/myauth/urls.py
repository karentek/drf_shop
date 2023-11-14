from django.urls import path
from django.conf import settings
from django.conf.urls import static
from .views import (SignInView,
                    SignUpView,
                    LogoutView,
                    ProfileUpdateView,
                    PostAvatarView,
                    PostPasswordView,
)


app_name = "myauth"


urlpatterns = [
    path("sign-in", SignInView.as_view(), name='sign-in'),
    path("sign-up", SignUpView.as_view(), name='sign-up'),
    path("sign-out", LogoutView.as_view(), name='sign-out'),

    path("profile", ProfileUpdateView.as_view()),
    path("profile/avatar", PostAvatarView.as_view(), name='post-avatar'),
    path("profile/password", PostPasswordView.as_view(), name='post-password'),


]


