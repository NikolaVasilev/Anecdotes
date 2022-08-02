from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from Anecdotes.models import Anecdote, Comment
from Anecdotes.queries import all_anecdotes, get_rate_by_id, get_reaction_by_id
from Anecdotes.serializers import AnecdoteSerializer, AnecdoteDetailSerializer, CommentSerializer, RateSerializer, \
    ReactionSerializer
from Anecdotes.utils import is_reaction_exist

from PersonalProjectRewiew.custom_permissions import IsGetOrIsAuthenticated, IsOwnerOrIsAdmin


class AnecdoteApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsGetOrIsAuthenticated]

    def get(self, request):
        anecdotes = all_anecdotes()
        serializer = AnecdoteSerializer(anecdotes, many=True)

        return Response(serializer.data)

    def post(self, request):
        user = request.user
        request.data['created_by'] = user.id
        serializer = AnecdoteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnecdoteDetailsApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrIsAdmin]

    def get_object(self, request, id):
        anecdote = get_object_or_404(Anecdote, id=id)
        self.check_object_permissions(request, anecdote)
        return anecdote

    def get(self, request, id):
        anecdote = self.get_object(request, id)
        serializer = AnecdoteDetailSerializer(anecdote)
        return Response(serializer.data)

    def put(self, request, id):
        anecdote = self.get_object(request, id)
        request.data['created_by'] = anecdote.created_by.id

        serializer = AnecdoteSerializer(anecdote, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        anecdote = self.get_object(request, id)
        anecdote.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrIsAdmin]

    def get_anecdote(self, id):
        return get_object_or_404(Anecdote, id=id)

    def get_object(self, request, id):
        comment = get_object_or_404(Comment, id=id)
        self.check_object_permissions(request, comment)
        return comment

    def get_user(self, request):
        return request.user

    def post(self, request, id):
        user = self.get_user(request)
        request.data['anecdote_id'] = id
        request.data['created_by'] = user.id
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        comment = self.get_object(request, request.data['id'])
        request.data['anecdote_id'] = id
        request.data['created_by'] = comment.created_by.id


        serializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        self.get_object(request, request.data['id']).delete()
        self.get_anecdote(id).save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RateApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrIsAdmin]

    def get_anecdote(self, id):
        return get_object_or_404(Anecdote, id=id)

    def post(self, request, id):
        user_id = request.user.id
        anecdote_id = id

        request.data['user'] = user_id
        request.data['anecdote'] = anecdote_id

        serializer = RateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        request.data['anecdote'] = id
        rate = get_rate_by_id(request.data['id'])
        request.data['user'] = rate.user.id

        self.check_object_permissions(request, rate)
        serializer = RateSerializer(rate, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        rate = get_rate_by_id(request.data['id'])
        self.check_object_permissions(request, rate)
        rate.delete()
        self.get_anecdote(id).save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReactionApiView(APIView):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_anecdote(self, id):
        return get_object_or_404(Anecdote, id=id)

    # This post method performs 2 operations - Create, if reaction doesnt exist or Delete, if reaction exist
    # This allows FE to use same request for these operations
    # Марто идеята я краднах от фейса :D - да не кажеш че ползвам пост за делийт операции,
    # пък и ползвам композитен ключ така че реално ид на записа не ми трябва никъде :D :D

    def post(self, request, id):
        user_id = request.user.id
        anecdote_id = id

        if is_reaction_exist(request.data['reaction'], user_id, anecdote_id):
            reaction = get_reaction_by_id(request.data['reaction'], user_id, anecdote_id)
            anecdote = self.get_anecdote(id)

            reaction.delete()
            anecdote.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        request.data['user'] = user_id
        request.data['anecdote'] = anecdote_id

        serializer = ReactionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------ another option is to use post and delete requests for reactions but is not necessary -------

    # def delete(self, request, id):
    #     user_id = request.user.id
    #     anecdote = self.get_anecdote(id)
    #     reaction = get_reaction_by_id(request.data['reaction'], user_id, anecdote.id)

    #     reaction.delete()
    #     anecdote.save()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------------------------------------------------------------------------------------------------
