from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from .models import *
import datetime


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
        user = User.objects.create(email=validated_data['email'],)
        user.set_password(validated_data['password'])

        user.save()
        return user

class CheckUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    status = serializers.CharField(max_length=64)


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


class TravelSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=64)
    place_name = serializers.CharField(max_length=64)
    start_year = serializers.IntegerField()
    start_month = serializers.IntegerField()
    start_day = serializers.IntegerField()
    end_year = serializers.IntegerField()
    end_month = serializers.IntegerField()
    end_day = serializers.IntegerField()

    def create(self, validated_data):
        start_date_fd = datetime.date(validated_data['start_year'], validated_data['start_month'], validated_data['start_day'])
        end_date_fd = datetime.date(validated_data['end_year'], validated_data['end_month'], validated_data['end_day'])

        travel = Travel.objects.create(title=validated_data['title'], place_name=validated_data['place_name'], start_date=start_date_fd, end_date=end_date_fd)
        travel.save()
        return validated_data;
