from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    UserView,
    GetUserByUsername,
    users_recommended,
    follow_user,
    profile_avatar_update,
    profile_info_update,
    get_followers,
    remove_follower,
)

urlpatterns = [
    path('register', UserRegisterView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),
    path('user', UserView.as_view(), name='user'),
    path('user/<str:username>', GetUserByUsername.as_view(), name='get-user'),
    path('users-recommended', users_recommended, name='users-recommended'),
    path('follow/<str:username>', follow_user, name='follow-user'),
    path('remove-follower/<str:username>',
         remove_follower, name='remove-follower'),
    path('update-avatar', profile_avatar_update, name='update-avatar'),
    path('update-info', profile_info_update, name='update-info'),
    path('get-followers/<str:username>', get_followers, name='get-followers'),
]
