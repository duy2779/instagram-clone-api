from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserLoginSerializer
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
