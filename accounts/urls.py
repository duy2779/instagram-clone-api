from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    UserView,
    GetUserByUsername,
    users_recommended,
    follow_user,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

urlpatterns = [
    path('register', UserRegisterView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('user', UserView.as_view(), name='user'),
    path('get-user', GetUserByUsername.as_view(), name='get-user'),
    path('users-recommended', users_recommended, name='users-recommended'),
    path('follow/<str:username>', follow_user, name='follow-user'),
]
