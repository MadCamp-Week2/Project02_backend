from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http.response import HttpResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


# Create your views here.
class NotificationView(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated,]
    authentication_classes = [JSONWebTokenAuthentication]
    # permission_classes = [permissions.AllowAny,]


@api_view(['POST'])
@permission_classes([AllowAny])
def createUser(request):
    if request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            print("here")
            return Response(serializer.data, 409)

        if User.objects.filter(email=serializer.validated_data['email']).first() is None:
            serializer.save()
            return Response(serializer.data, 201)
        print("here22")
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

        # response = {
        #     'success': 'True',
        #     'token': serializer.data['token']
        # }
        return Response(serializer.data, 200)
