from django.urls import path

from .views import(
    get_notifications
)

urlpatterns = [
    path('get-notifications', get_notifications, name='get-notifications')
]
