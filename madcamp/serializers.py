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

class PlaceSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    address = serializers.CharField()

class NotificationSerializer(serializers.ModelSerializer):
    # creator = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        # fields = ('id', 'title', 'content', 'creator', 'datetime')
        fields = ('id', 'title', 'content')

User = get_user_model()

class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    profile_image = serializers.CharField(required=False)

    def create(self, validated_data):
        user = User.objects.create(email=validated_data['email'])
        user.set_password(validated_data['password'])

        user.save()

        profile = Profile.objects.create(user=user, name=validated_data['username'], photo=validated_data['profile_image'])
        profile.save()

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
    travel_id = serializers.IntegerField()
    title = serializers.CharField(max_length=64)
    place_name = serializers.CharField(max_length=64)
    start_year = serializers.IntegerField()
    start_month = serializers.IntegerField()
    start_day = serializers.IntegerField()
    end_year = serializers.IntegerField()
    end_month = serializers.IntegerField()
    end_day = serializers.IntegerField()
    user_emails = serializers.EmailField(required=True)

    def create(self, validated_data):
        start_date_fd = datetime.date(validated_data['start_year'], validated_data['start_month'], validated_data['start_day'])
        end_date_fd = datetime.date(validated_data['end_year'], validated_data['end_month'], validated_data['end_day'])

        travel = Travel.objects.create(title=validated_data['title'], place_name=validated_data['place_name'], start_date=start_date_fd, end_date=end_date_fd)
        travel.save()

        user = User.objects.filter(email = validated_data['user_emails']).first()
        profile = Profile.objects.get(user = user)
        profile.travels.add(travel)

        validated_data['travel_id'] = travel.id
        return validated_data


class newScheduleSeralizer(serializers.Serializer):
    travel_id = serializers.IntegerField()
    day = serializers.IntegerField()
    money = serializers.IntegerField()
    memo = serializers.CharField(allow_null=True, allow_blank=True)
    start_hour = serializers.IntegerField()
    start_minute = serializers.IntegerField()
    end_hour = serializers.IntegerField()
    end_minute = serializers.IntegerField()
    place_name = serializers.CharField()
    place_address = serializers.CharField()
    schedule_id = serializers.IntegerField()

    def create(self, validated_data):
        start_time = datetime.time(hour=validated_data['start_hour'], minute=validated_data['start_minute'])
        end_time = datetime.time(hour=validated_data['end_hour'], minute=validated_data['end_minute'])
        
        if Place.objects.filter(name=validated_data['place_name']).first() is None:
            place = Place.objects.create(name=validated_data['place_name'], address=validated_data['place_address'])
            place.save()

        place = Place.objects.filter(name=validated_data['place_name']).first()
        place.address = validated_data['place_address']
        place.save()

        travel = Travel.objects.filter(id=validated_data['travel_id']).first()
        
        if validated_data['schedule_id'] == -1 or Schedule.objects.get(id=validated_data['schedule_id']) is None:
            schedule = Schedule.objects.create(travel=travel, day=validated_data['day'], money=validated_data['money'], memo=validated_data['memo'], start_datetime=start_time, end_datetime=end_time, place=place)
        else:
            schedule = Schedule.objects.get(id=validated_data['schedule_id'])
            schedule.money = validated_data['money']
            schedule.memo = validated_data['memo']
            schedule.start_datetime = start_time
            schedule.end_datetime = end_time
            schedule.place = place
        
        schedule.save()

        validated_data['schedule_id'] = schedule.id
        return validated_data

class getTravelSerializer(serializers.Serializer):
    travel_id = serializers.IntegerField(required=True)
    title = serializers.CharField(max_length=64)
    place_name = serializers.CharField(max_length=64)
    start_year = serializers.IntegerField()
    start_month = serializers.IntegerField()
    start_day = serializers.IntegerField()
    end_year = serializers.IntegerField()
    end_month = serializers.IntegerField()
    end_day = serializers.IntegerField()
    schedule_list = newScheduleSeralizer(many=True)


class userTravelSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    travel_list = getTravelSerializer(many=True)


class updateTravelSerializer(serializers.Serializer):
    travel_id = serializers.IntegerField(required=True)
    title = serializers.CharField()
    place_name = serializers.CharField()

    def create(self, validated_data):
        if validated_data['travel_id'] < 0 or Travel.objects.get(id = validated_data['travel_id']) is None:
            raise serializers.ValidationError(
                'According Travel object does not exist!'
            )
        travel = Travel.objects.get(id = validated_data['travel_id'])
        
        travel.title = validated_data['title']
        travel.place_name = validated_data['place_name']
        travel.save()

        return validated_data