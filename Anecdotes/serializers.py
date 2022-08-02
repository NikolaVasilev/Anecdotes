from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import serializers

from Anecdotes.models import Anecdote, Category, Comment, Rating, Reactions


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class BaseCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_by', 'created_at', 'updated_at']


class CommentSerializer(BaseCommentSerializer):
    anecdote_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ['id', 'anecdote_id', 'content', 'created_by']

    @transaction.atomic
    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        anecdote = Anecdote.objects.get(id=validated_data['anecdote_id'])
        anecdote.comment_set.add(comment)
        anecdote.save()
        return comment

    @transaction.atomic
    def update(self, instance, validated_data):
        Comment.objects.select_for_update().filter(id=instance.id).update(**validated_data)
        comment = Comment.objects.select_for_update().get(id=instance.id)
        anecdote = Anecdote.objects.get(id=validated_data['anecdote_id'])
        anecdote.comment_set.set([comment])
        anecdote.save()
        return comment


class CommentDetailSerializer(BaseCommentSerializer):
    created_by = UserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_by', 'created_at', 'updated_at']


class BaseAnecdoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anecdote
        fields = ['id', 'name', 'content', 'categories', 'created_at', 'updated_at', 'created_by']


class AnecdoteSerializer(BaseAnecdoteSerializer):
    @transaction.atomic
    def create(self, validated_data):
        categories = validated_data.pop('categories')
        anecdote = Anecdote.objects.create(**validated_data)
        anecdote.categories.set(categories)
        anecdote.save()
        return anecdote

    @transaction.atomic
    def update(self, instance, validated_data):
        categories = validated_data.pop('categories')
        Anecdote.objects.select_for_update().filter(id=instance.id).update(**validated_data)
        anecdote = Anecdote.objects.select_for_update().get(id=instance.id)
        if categories is not None:
            anecdote.categories.set(categories)
        anecdote.save()
        return anecdote


class AnecdoteDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    categories = CategorySerializer(many=True)
    comments = CommentDetailSerializer(source='comment_set', many=True, read_only=True)

    class Meta:
        model = Anecdote
        fields = ['id', 'name', 'content', 'created_at', 'updated_at', 'created_by', 'rate', 'categories', 'reactions',
                  'comments']


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user', 'anecdote', 'rate']

    @transaction.atomic
    def create(self, validated_data):
        rate = Rating.objects.create(**validated_data)
        anecdote = validated_data['anecdote']
        anecdote.rating_set.set([rate])
        anecdote.save()
        return rate

    @transaction.atomic
    def update(self, instance, validated_data):
        Rating.objects.select_for_update().filter(id=instance.id).update(**validated_data)
        anecdote = validated_data['anecdote']
        anecdote.save()
        return validated_data


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reactions
        fields = ['id', 'user', 'anecdote', 'reaction']

    @transaction.atomic
    def create(self, validated_data):
        reaction = Reactions.objects.create(**validated_data)
        anecdote = validated_data['anecdote']
        anecdote.reactions_set.set([reaction])
        anecdote.save()
        return reaction
