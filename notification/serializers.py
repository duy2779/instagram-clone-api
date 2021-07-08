from rest_framework import serializers
from .models import Notification

from accounts.serializers import UserPreviewSerializer
from post.serializers import PostNotificationSerializer


class NotificationSerializer(serializers.ModelSerializer):
    created_by = UserPreviewSerializer(many=False)
    post = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'

    def get_post(self, obj):
        if obj.notification_type != 'follow':
            return PostNotificationSerializer(obj.post, many=False).data
        return None