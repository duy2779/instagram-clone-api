from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes

from .models import Notification
from .serializers import NotificationSerializer

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def mark_notifications_seen(request):
    user = request.user
    Notification.objects.filter(user=user, seen=False).update(seen=True)
    return Response("Mark notifications successfully")