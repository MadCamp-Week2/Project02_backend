from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class NotificationSerializer(serializers.ModelSerializer):
    # creator = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        # fields = ('id', 'title', 'content', 'creator', 'datetime')
        fields = ('id', 'title', 'content')

#might be redundant
class AccountInfoSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()

    def save(self):
        email = self.validated_data['email']
        name = self.validated_data['name']
        user = User()
        user.email = email
        user.save()
        profile = Profile()
        profile.name = name
        profile.save()


User = get_user_model()

class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])

        user.save()
        return user

class CheckUserSerializer(serializer.Serializer):
    email = serializers.EmailField(required=True)
    status = serializers.CharField(max_length=64)

    def create(self, validated_data):
        email=validated_data['email']
        if User.objects.filter(email=validated_data['email']).first() is None:
            status = "False"
        else:
            status = "True"


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)

        if user is None:
            return {
                'email': 'None'
            }
        try:
            jwt_token = RefreshToken.for_user(user).access_token
            update_last_login(None, user)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {
            'email': user.email,
            'token': jwt_token
        }
