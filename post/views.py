from django.shortcuts import render
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Post, PostComment
from .serializers import PostSerializer, PostCommentSerializer

# Create your views here.


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_posts(request):
    user = request.user
    users_following = user.following.all()
    posts = Post.objects.filter(Q(user=user) | Q(
        user__in=users_following)).order_by('-created')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)
