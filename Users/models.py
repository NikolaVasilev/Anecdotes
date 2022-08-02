from django.contrib.auth.models import PermissionsMixin, User
from django.core.mail import send_mail
from django.db import models

# Create your models here.
from rest_framework.authtoken.models import Token


class User(User):
    class Meta:
        proxy = True
        ordering = ('username',)

    @property
    def token(self):
        return Token.objects.get(user_id=self.id)
