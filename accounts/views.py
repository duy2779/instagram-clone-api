import os.path
import uuid
import random
from urllib.error import HTTPError

from django.core.files.storage import default_storage
from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib.auth import authenticate

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from social_django.utils import load_strategy, load_backend

from notification.models import Notification

from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserPreviewSerializer
)
from .models import User


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['password'] = make_password(
                serializer.validated_data['password'])
            user = serializer.save()

            return JsonResponse({
                'message': 'Register successful!'
            }, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({
                'error_message': serializer.errors,
                'error_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ), responses={"200": openapi.Response(description="Success"), })
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            if User.objects.filter(username=username).exists() == False:
                return Response("The username you entered doesn't belong to an account. Please check your username and try again.",
                                status=status.HTTP_400_BAD_REQUEST)
            user = authenticate(request, username=username, password=password)
            if user:
                refresh = TokenObtainPairSerializer.get_token(user)
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
                return Response(data, status=status.HTTP_200_OK)
            return Response('Sorry, your password was incorrect. Please double-check your password.',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, many=False)
        return Response(serializer.data)


class GetUserByUsername(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        except Exception as e:
            return Response(f'{e}', status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def users_recommended(request):
    """
    Get users order by followers_count and
    exclude the users that the user has followed
    """
    user = request.user
    users_following = [user.id for user in user.following.all()]
    # added the user to list that not get for users recommended
    users_following.append(user.id)

    users = User.objects.annotate(followers_count=Count('followers')).order_by(
        'followers_count').reverse().exclude(id__in=users_following)[0:5]
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def follow_user(request, username):
    user = request.user
    try:
        user_to_follow = User.objects.get(username=username)

        if user == user_to_follow:
            return Response('You can not follow yourself', status=status.HTTP_400_BAD_REQUEST)

        if user in user_to_follow.followers.all():
            user_to_follow.followers.remove(user)
            user_to_follow.save()
            serializer = UserSerializer(user, many=False)

            Notification.objects.filter(
                user=user_to_follow,
                created_by=user,
                notification_type='follow'
            ).delete()
            return Response({'type': 'follow', 'user': serializer.data})
        else:
            user_to_follow.followers.add(user)
            user_to_follow.save()
            serializer = UserSerializer(user, many=False)

            Notification.objects.create(
                user=user_to_follow,
                created_by=user,
                notification_type='follow',
                content=f"{user} followed {user_to_follow}"
            )
            return Response({'type': 'unfollow', 'user': serializer.data})
    except Exception as e:
        message = {'detail': e}
        return Response(f'{message}', status=status.HTTP_204_NO_CONTENT_)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def remove_follower(request, username):
    user = request.user
    try:
        follower_to_remove = User.objects.get(username=username)

        if user == follower_to_remove:
            return Response('You can not remove yourself', status=status.HTTP_400_BAD_REQUEST)

        user.followers.remove(follower_to_remove)
        user.save()
        serializer = UserSerializer(user, many=False)
        return Response({'message':f'remove {username} successfully', 'user':serializer.data})
    except Exception as e:
        message = {'detail': e}
        return Response(f'{message}', status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
@parser_classes([MultiPartParser, FormParser])
def profile_avatar_update(request):
    rd = random.Random()
    avatar_pic = request.FILES['avatar']
    extension = os.path.splitext(avatar_pic.name)[1]
    avatar_pic.name = '{}{}'.format(
        uuid.UUID(int=rd.getrandbits(128)), extension)
    filename = default_storage.save(avatar_pic.name, avatar_pic)
    setattr(request.user, 'avatar_pic', filename)
    serializer = UserSerializer(request.user, data={}, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        response = {'type': 'Success', 'message': 'successfully updated your info',
                    'user': UserSerializer(user).data}
    else:
        response = serializer.errors
    return Response(response)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def profile_info_update(request):
    serializer = UserSerializer(
        request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        response = {'type': 'Success', 'message': 'successfully updated your info',
                    'user': UserSerializer(user).data}
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(response)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_followers(request, username):
    try:
        user = User.objects.get(username=username)
        followers = user.followers.all()
        serializer = UserPreviewSerializer(followers, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_following(request, username):
    try:
        user = User.objects.get(username=username)
        following = user.following.all()
        serializer = UserPreviewSerializer(following, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_users(request):
    query = request.query_params.get('q')
    query = query.strip()
    if query == '':
        user = []
    else:
        user = User.objects.filter(
            Q(username__icontains=query) |
            Q(full_name__icontains=query)
        ).annotate(followers_count=Count('followers')).order_by(
            'followers_count').reverse()
    serializer = UserSerializer(user, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def social_login(request):
    strategy = load_strategy(request)

    backend = load_backend(strategy=strategy, name='facebook',
                           redirect_uri=None)
    try:
        if isinstance(backend, BaseOAuth2):
            access_token = request.POST.get('access_token')
            print("access_token:", access_token)
        user = backend.do_auth(access_token)
    except HTTPError as error:
        return Response({
            "error": {
                "access_token": "Invalid token",
                "details": str(error)
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    except AuthTokenError as error:
        return Response({
            "error": "Invalid credentials",
            "details": str(error)
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        authenticated_user = backend.do_auth(access_token, user=user)

    except HTTPError as error:
        return Response({
            "error": "invalid token",
            "details": str(error)
        }, status=status.HTTP_400_BAD_REQUEST)

    except AuthForbidden as error:
        return Response({
            "error": "invalid token",
            "details": str(error)
        }, status=status.HTTP_400_BAD_REQUEST)

    if authenticated_user and authenticated_user.is_active:
        refresh = TokenObtainPairSerializer.get_token(authenticated_user)
        is_new = False
        if not authenticated_user.email:
            is_new = True
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_new': is_new,
        }
        return Response(data, status=status.HTTP_200_OK)
