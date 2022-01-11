from django.contrib import auth
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http.response import HttpResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers

# Create your views here.
class NotificationView(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated,]
    # permission_classes = [permissions.AllowAny,]

@api_view(['GET'])
@permission_classes([AllowAny])
def checkUser(request):
    if request.method == 'GET':
        email = request.query_params.get('params1',None)
        data = {'email':email, 'status':''}
        if User.objects.filter(email=email).first() is None:
            data['status'] = "False"
        else:
            data['status'] = "True"

        serializer = CheckUserSerializer(data=data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.data, 409)

        return Response(serializer.data, 200)

@api_view(['POST'])
@permission_classes([AllowAny])
def createUser(request):
    if request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.data, 409)

        if User.objects.filter(email=serializer.validated_data['email']).first() is None:
            serializer.save()
            return Response(serializer.data, 201)
        return Response(serializer.data, 409)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.data, 409)
        if serializer.validated_data['email'] == "None":
            return Response(serializer.data, 200)

        return Response(serializer.data, 200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_travel(request):
    if request.method == 'POST':
        serializer = TravelSerializer(data=request.data)
        # print(request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)

        serializer.save()
        # print(serializer.data)
        return Response(serializer.data, 201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_travel(request):
    if(request.method == 'GET'):
        # print(request.query_params.get('params1',None))
        email = request.query_params.get('params1',None)
        user = User.objects.filter(email=email).first()
        # print(user)
        profile = Profile.objects.get(user=user)
        travel_list = []
        # print(profile.travels.all())
        for travel in profile.travels.all():
            schedule_list = []
            for schedule in Schedule.objects.filter(travel=travel):
                schedule_list.append({"travel_id":travel.id, "day":schedule.day, "money":schedule.money, "memo":schedule.memo, "start_hour":schedule.start_datetime.hour, "start_minute":schedule.start_datetime.minute, "end_hour":schedule.end_datetime.hour, "end_minute":schedule.end_datetime.minute, "place_name":schedule.place.name, "place_address":schedule.place.address, "schedule_id":schedule.id})
            travel_list.append({"travel_id":travel.id, "title":travel.title, "place_name":travel.place_name, "start_year":travel.start_date.year, "start_month":travel.start_date.month, "start_day":travel.start_date.day, "end_year":travel.end_date.year, "end_month":travel.end_date.month, "end_day":travel.end_date.day, "schedule_list":schedule_list})
        
        # print(travel_list)
        serializer = userTravelSerializer(data={'email':email, 'travel_list':travel_list})
        # print(serializer.initial_data)

        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)

        return Response(serializer.data, 200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_schedule(request):
    if request.method == 'POST':
        # print(request.data)
        serializer = newScheduleSeralizer(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)
        
        serializer.save()
        return Response(serializer.data, 201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def del_schedule(request):
    if request.method == 'POST':
        # print(request.data)
        del_id = request.data
        if del_id is None or del_id < 0 or Schedule.objects.filter(id = del_id).first() is None:
            return Response(request.data, 409)
        
        Schedule.objects.filter(id = del_id).delete()

        return Response(request.data, 200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_travel(request):
    if request.method == 'POST':
        serializer = updateTravelSerializer(data=request.data)
        
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.data, 409)
        
        serializer.save() # serializer.self.instance not initialized, so create method called instead of update method

        return Response(serializer.data, 201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def del_travel(request):
    if request.method == 'POST':
        del_id = request.data
        if del_id is None or del_id < 0 or Travel.objects.filter(id = del_id).first() is None:
            return Response(request.data, 409)
        
        Travel.objects.filter(id = del_id).delete()

        return Response(request.data, 200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends(request):
    if request.method == 'GET':
        email = request.query_params.get('params1',None)
        
        if email is None or User.objects.filter(email=email).first() is None:
            return Response({'email':email, friend_list:[]}, 409)
        
        from_user = User.objects.filter(email=email).first()
        friend_list = []
        
        for friend in Profile.objects.get(user=from_user).friends.all():
            friend_list.append({'username':friend.name, 'email':friend.user.email, 'photo':friend.photo})
        
        serializer = getFriendsSerializer(data={'email':email, 'friend_list':friend_list})
        
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.data, 409)
        
        return Response(serializer.data, 200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friend_requests(request):
    if request.method == 'GET':
        email = request.query_params.get('params1',None)
        if email is None or User.objects.filter(email=email).first() is None:
            return Response({'email':email, friend_list:[]}, 409)

        from_user = User.objects.filter(email=email).first()
        friend_request_list = []

        for friend_request in Profile.objects.get(user=from_user).pending_requests.all():
            friend_request_list.append({'username':friend_request.name, 'email':friend_request.user.email, 'photo':friend_request.photo})

        serializer = getFriendsSerializer(data={'email':email, 'friend_list':friend_request_list})

        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.data, 409)

        return Response(serializer.data, 200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_friend_request(request):
    if request.method == 'POST':
        serializer = FriendRequestSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)
        
        serializer.save()

        return Response(serializer.data, 201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_or_ignore_friend(request):
    if request.method == "POST":
        serializer = FriendAddorIgnoreRequestSerializer(data=request.data)
        
        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)
        
        serializer.save()

        return Response(serializer.data, 201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def del_friend(request):
    if request.method == 'POST':
        serializer = FriendDeleteSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)

        serializer.save()

        return Response(serializer.data, 201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_travel_request(request):
    if request.method == 'POST':
        serializer = TravelRequestSerializer(data=request.data)
        print(request.data)
        
        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)

        serializer.save()

        return Response(serializer.data, 201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_or_ignore_travel(request):
    if request.method == 'POST':
        serializer = TravelAddorIgnoreRequestSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)

        serializer.save()

        return Response(serializer.data, 201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_travel_requests(request):
    if request.method == 'GET':
        email = request.query_params.get('params1',None)
        if email is None or User.objects.filter(email=email).first() is None:
            return Response({'email':email, travel_list:[]}, 409)

        user = User.objects.filter(email=email).first()
        travel_request_list = []

        for travel_request in Profile.objects.get(user=user).pending_travels.all():
            schedule_list = []
            for schedule in Schedule.objects.filter(travel=travel_request):
                schedule_list.append({"travel_id":travel_request.id, "day":schedule.day, "money":schedule.money, "memo":schedule.memo, "start_hour":schedule.start_datetime.hour, "start_minute":schedule.start_datetime.minute, "end_hour":schedule.end_datetime.hour, "end_minute":schedule.end_datetime.minute, "place_name":schedule.place.name, "place_address":schedule.place.address, "schedule_id":schedule.id})
            travel_request_list.append({"travel_id":travel_request.id, "title":travel_request.title, "place_name":travel_request.place_name, "start_year":travel_request.start_date.year, "start_month":travel_request.start_date.month, "start_day":travel_request.start_date.day, "end_year":travel_request.end_date.year, "end_month":travel_request.end_date.month, "end_day":travel_request.end_date.day, "schedule_list":schedule_list})

        serializer = userTravelSerializer(data={'email':email, 'travel_list':travel_request_list})

        if not serializer.is_valid(raise_exception=False):
            return Response(serializer.data, 409)

        return Response(serializer.data, 200)