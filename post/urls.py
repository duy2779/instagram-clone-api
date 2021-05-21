from django.urls import path

from .views import get_posts

urlpatterns = [
    path('posts', get_posts, name='posts')
]
