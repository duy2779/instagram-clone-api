from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
        user = User.objects.get(username=username)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


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
            return Response('You can not follow yourself')

        if user in user_to_follow.followers.all():
            user_to_follow.followers.remove(user)
            user_to_follow.save()
            return Response('User unfollowed')
        else:
            user_to_follow.followers.add(user)
            user_to_follow.save()
            return Response('User followed')
    except Exception as e:
        message = {'detail': e}
        return Response(message, status=status.HTTP_204_NO_CONTENT_)
