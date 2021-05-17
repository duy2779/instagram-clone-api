from django.urls import path
from .views import UserRegisterView, UserLoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

urlpatterns = [
    path('register', UserRegisterView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
]
