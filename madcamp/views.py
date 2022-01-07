from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http.response import HttpResponse
from rest_framework.permissions import AllowAny


# Create your views here.
class NotificationView(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes = [permissions.IsAuthenticated,]
    permission_classes = [permissions.AllowAny,]


@api_view(['POST'])
@permission_classes([AllowAny])
def createUser(request):
    if request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_409_CONFLICT)

        if User.objects.filter(email=serializer.validated_data['email']).first() is None:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response({"message": "Request Body Error."}, status=status.HTTP_409_CONFLICT)
        if serializer.validated_data['email'] == "None":
            return Response({'message': 'fail'}, status=status.HTTP_200_OK)

        response = {
            'success': 'True',
            'token': serializer.data['token']
        }
        return Response(response, status=status.HTTP_200_OK)
