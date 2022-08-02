from django.http import Http404
from rest_framework import serializers

from Anecdotes.models import Anecdote, Rating, Reactions


def all_anecdotes():
    return Anecdote.objects.all()


def anecdotes_by_user_id(id):
    return Anecdote.objects.filter(created_by=id)


def get_rate_by_id(id):
    try:
        return Rating.objects.get(id=id)

    except Rating.DoesNotExist:
        raise Http404


def get_reaction_by_id(reaction_id, user_id, anecdote_id):
    try:
        return Reactions.objects.get(
            reaction_id=reaction_id,
            user_id=user_id,
            anecdote_id=anecdote_id)

    except Reactions.DoesNotExist:
        return Reactions.objects.none
