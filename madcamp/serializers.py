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

        user = User.objects.filter(email = validated_data['user_emails']).first()
        profile = Profile.objects.get(user=user)
        
        travel = Travel.objects.create(title=validated_data['title'], place_name=validated_data['place_name'], start_date=start_date_fd, end_date=end_date_fd)
        travel.participants.add(profile)

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


class FriendSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    photo = serializers.CharField()


class getFriendsSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    friend_list = FriendSerializer(many=True)


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
    participant_list = FriendSerializer(many=True)


class userTravelSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    travel_list = getTravelSerializer(many=True)

class FriendRequestSerializer(serializers.Serializer):
    from_user_email = serializers.EmailField()
    to_user_email = serializers.EmailField()
    status = serializers.CharField()

    def create(self, validated_data):
        from_user = User.objects.filter(email=validated_data['from_user_email']).first()
        to_user = User.objects.filter(email=validated_data['to_user_email']).first()
        
        from_user_profile = Profile.objects.get(user=from_user)
        # print(Profile.objects.get(user=to_user).pending_requests.all())

        if to_user is None:
            validated_data['status'] = 'False'
        elif from_user.id == to_user.id:
            validated_data['status'] = 'Self'
        elif Profile.objects.get(user=from_user).pending_requests.all().filter(user=to_user).first() is not None:
            validated_data['status'] = 'Onrequest'
        elif Profile.objects.get(user=to_user).pending_requests.all().filter(user=from_user).first() is not None:
            validated_data['status'] = 'Duplicated'
        elif from_user_profile.friends.all().filter(user=to_user).first() is not None:
            validated_data['status'] = 'Already'
        else:
            validated_data['status']  = 'True'
            to_user_profile = Profile.objects.get(user=to_user)
            to_user_profile.pending_requests.add(from_user_profile)
        
        return validated_data

class FriendAddorIgnoreRequestSerializer(serializers.Serializer):
    from_user_email = serializers.EmailField()
    to_user_email = serializers.EmailField()
    status = serializers.CharField()

    def create(self, validated_data):
        from_user = User.objects.filter(email=validated_data['from_user_email']).first()
        to_user = User.objects.filter(email=validated_data['to_user_email']).first()
        
        from_user_profile = Profile.objects.get(user=from_user)
        to_user_profile = Profile.objects.get(user=to_user)
        
        to_user_profile.pending_requests.remove(from_user_profile) #remove relation from many to many field
        
        if validated_data['status'] == 'ACCEPT':
            to_user_profile.friends.add(from_user_profile)
            from_user_profile.friends.add(to_user_profile)

        return validated_data

class FriendDeleteSerializer(serializers.Serializer):
    from_user_email = serializers.EmailField()
    to_user_email = serializers.EmailField()
    status = serializers.CharField()

    def create(self, validated_data):
        from_user = User.objects.filter(email=validated_data['from_user_email']).first()
        to_user = User.objects.filter(email=validated_data['to_user_email']).first()
        
        from_user_profile = Profile.objects.get(user=from_user)
        to_user_profile = Profile.objects.get(user=to_user)

        to_user_profile.friends.remove(from_user_profile)
        from_user_profile.friends.remove(to_user_profile)

        validated_data['status'] = "REMOVED"
        
        return validated_data

class TravelRequestSerializer(serializers.Serializer):
    from_user_email = serializers.EmailField()
    to_user_emails = serializers.ListField(child=serializers.EmailField())
    travel_id = serializers.IntegerField()

    def create(self, validated_data):
        from_user = User.objects.filter(email=validated_data['from_user_email']).first()
        from_user_profile = Profile.objects.get(user=from_user)
        request_travel = Travel.objects.get(id=validated_data['travel_id'])
        
        to_user_email_list = validated_data['to_user_emails']
        for to_user_email in to_user_email_list:
            to_user = User.objects.filter(email=to_user_email).first()
            to_user_profile = Profile.objects.get(user=to_user)
            to_user_profile.pending_travels.add(request_travel)
        return validated_data

class TravelAddorIgnoreRequestSerializer(serializers.Serializer):
    to_user_email = serializers.EmailField()
    travel_id = serializers.IntegerField()
    status = serializers.CharField()

    def create(self, validated_data):
        to_user = User.objects.filter(email=validated_data['to_user_email']).first()
        to_user_profile = Profile.objects.get(user=to_user)
        pending_travel = Travel.objects.get(id=validated_data['travel_id'])
        
        to_user_profile.pending_travels.remove(pending_travel) #remove relation from many to many field

        if validated_data['status'] == 'ACCEPT':
            pending_travel.participants.add(to_user_profile)
            to_user_profile.travels.add(pending_travel)

        return validated_data