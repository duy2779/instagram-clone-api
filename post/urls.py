from django.urls import path

from .views import get_posts, toggle_like

urlpatterns = [
    path('posts', get_posts, name='posts'),
    path('toggle-like/<str:post_id>', toggle_like, name='toggle-like'),
]
