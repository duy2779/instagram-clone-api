from django.urls import path

from .views import get_posts, toggle_like, add_comment, create_post

urlpatterns = [
    path('posts', get_posts, name='posts'),
    path('toggle-like/<str:post_id>', toggle_like, name='toggle-like'),
    path('add-comment/<str:post_id>', add_comment, name='add-comment'),
    path('create-post', create_post, name='create-post'),
]
