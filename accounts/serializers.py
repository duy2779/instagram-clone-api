from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    avatar_pic = serializers.SerializerMethodField(read_only=True)
    posts_count = serializers.ReadOnlyField()
    unseen_notifications_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email',
                  'avatar_pic', 'following', 'followers', 'posts_count', 'unseen_notifications_count')

    def get_avatar_pic(self, obj):
        try:
            pic = obj.avatar_pic.url
        except:
            pic = None
        return pic


class UserPreviewSerializer(serializers.ModelSerializer):
    """
        Get base infomation of user for some component
        as user in followers, following, users_recommended...
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'avatar_pic')
