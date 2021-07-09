from django.shortcuts import render
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Post, PostComment
from .serializers import PostSerializer, PostCommentSerializer
from notification.models import Notification


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
            Notification.objects.filter(
                notification_type="like",
                user=post.user,
                created_by=user,
            ).delete()
            return Response('Post unliked')
        else:
            post.users_like.add(user)
            post.save()
            if user != post.user:
                Notification.objects.create(
                    user=post.user,
                    created_by=user,
                    notification_type='like',
                    post=post,
                    content=f"{user} liked a post by {post.user}"
                )
            return Response('Post liked')
    except Exception as e:
        message = {'detail': e}
        return Response(message, status=status.HTTP_204_NO_CONTENT_)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def add_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        comment = request.data.get('comment')
        post_comment = PostComment(
            post=post, user=request.user, comment=comment)
        post_comment.save()
        return Response("added comment successful", status=status.HTTP_201_CREATED)
    except Exception as e:
        message = {'detail': e}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@parser_classes([MultiPartParser, FormParser])
def create_post(request):
    user_id = request.data.get('user') or None
    caption = request.data.get('caption') or None
    image = request.data.get('image') or None
    post = Post.objects.create(
        user=request.user, caption=caption, image=image)
    serializer = PostSerializer(post, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_posts_by_username(request, username):
    posts = Post.objects.filter(user__username=username).order_by('-created')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if post.user == request.user:
            post.delete()
            return Response("delete a post successfully", status=status.HTTP_200_OK)
        else:
            return Response("You don't have permission to delete this post", status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'details': f"{e}"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_post_by_id(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        serializer = PostSerializer(post, many=False)
        return Response(serializer.data)
    except Exception as e:
        return Response({'details': f"{e}"}, status=status.HTTP_204_NO_CONTENT)
