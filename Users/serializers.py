from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token

from Users.models import User

# import time


# post - auth: False
from Users.utils import password_validation


class BaseUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password_conformation = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_conformation']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    @transaction.atomic
    def save(self, **kwargs):
        user = User(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
        )

        password = self.validated_data['password']
        password_conformation = self.validated_data['password_conformation']

        password_validation(password, password_conformation)

        user.set_password(password)
        user.save()
        self.create_auth_token(instance=user, created=True)
        return user

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)


# put - auth: True
class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_conformation']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        password_conformation = validated_data.pop('password_conformation')

        password_validation(password, password_conformation)

        # =================== just for test :) ============================

        # start_time = time.time()

        # instance.email = validated_data['email']
        # instance.username = validated_data['username']
        # instance.first_name = validated_data['first_name']
        # instance.last_name = validated_data['last_name']
        # instance.password = make_password(password)
        # instance.save()

        # print("--- %s seconds ---" % (time.time() - start_time))

        # ======== there is no time and sql query difference ==============

        User.objects.select_for_update().filter(id=instance.id).update(**validated_data,
                                                                       password=make_password(password))

        return validated_data


# AnecdoteUserSerializer - currently in anecdotes, also can be renamed in anecdotes

# UserDetailSerializer - get - auth: True
class UserDetailSerializer(UserSerializer):

    class Meta:
        model = User
        exclude = ['password']

