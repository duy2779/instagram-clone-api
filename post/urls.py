from django.urls import path

from .views import (
    get_posts,
    toggle_like,
    add_comment,
    create_post,
    get_posts_by_username,
    delete_post,
    get_post_by_id,
)

urlpatterns = [
    path('posts', get_posts, name='posts'),
    path('toggle-like/<str:post_id>', toggle_like, name='toggle-like'),
    path('add-comment/<str:post_id>', add_comment, name='add-comment'),
    path('create-post', create_post, name='create-post'),
    path('get-posts/<str:username>', get_posts_by_username,
         name='get-posts-by-username'),
    path('delete-post/<str:post_id>', delete_post, name='delete-post'),
    path('get-post/<str:post_id>', get_post_by_id, name='get-post'),
]
