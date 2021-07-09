from django.urls import path

from .views import(
    get_notifications,
    mark_notifications_seen
)

urlpatterns = [
    path('get-notifications', get_notifications, name='get-notifications'),
    path('mark-notifications-seen', mark_notifications_seen, name='mark-notifications-seen'),
]
