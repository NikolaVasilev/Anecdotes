from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Anecdotes.queries import anecdotes_by_user_id
from Anecdotes.serializers import BaseAnecdoteSerializer
from Users.models import User
from Users.serializers import BaseUserSerializer, UserSerializer, UserDetailSerializer

from PersonalProjectRewiew.custom_permissions import IsPostAndIsNotAuthenticated


class UserApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsPostAndIsNotAuthenticated]

    def get(self, request, response_=None, id=None):
        if id is None and response_ is None:
            id = request.user.id
            response_ = 'details'
        user = get_object_or_404(User, id=id)
        return getattr(self, f'handle_{response_.lower()}')(request, user)

    # should return detail user info response
    def handle_details(self, request, user):
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # should return anecdotes by user id
    def handle_anecdotes(self, request, user):
        queryset = anecdotes_by_user_id(user.id)
        serializer = BaseAnecdoteSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BaseUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user).key
            data = {
                'email': serializer.data['email'],
                'username': serializer.data['username'],
                'token': token
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEditApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data)

        if serializer.is_valid():
            serializer.update(serializer.instance, serializer.validated_data)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivateApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDeleteApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
