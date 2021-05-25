from django.shortcuts import render
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import Post, PostComment
from .serializers import PostSerializer, PostCommentSerializer


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_posts(request):
    user = request.user
    users_following = user.following.all()
    posts = Post.objects.filter(Q(user=user) | Q(
        user__in=users_following)).order_by('-created')
    paginator = PageNumberPagination()
    paginator.page_size = 5
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def toggle_like(request, post_id):
    user = request.user
    try:
        post = Post.objects.get(id=post_id)
        if user in post.users_like.all():
            post.users_like.remove(user)
            post.save()
            return Response('Post unliked')
        else:
            post.users_like.add(user)
            post.save()
            return Response('Post liked')
    except Exception as e:
        message = {'detail': e}
        return Response(message, status=status.HTTP_204_NO_CONTENT_)
