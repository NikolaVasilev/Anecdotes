from rest_framework import serializers


def password_validation(pass_01, pass_02):
    if pass_01 != pass_02:
        raise serializers.ValidationError({'password': 'Password should be the same as Password Conformation!'})
