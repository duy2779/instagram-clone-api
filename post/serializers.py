from rest_framework import serializers
from .models import Post, PostComment
from accounts.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    user = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ('__all__')

    def get_user(self, obj):
        user = obj.user
        serializer = UserSerializer(user, many=False)
        return serializer.data

    def get_comments(self, obj):
        comments = obj.comments.all()
        serializer = PostCommentSerializer(comments, many=True)
        return serializer.data


class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostComment
        fields = ('__all__')

    def get_user(self, obj):
        return obj.user.username
