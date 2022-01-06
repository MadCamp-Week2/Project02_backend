from django.shortcuts import render
from rest_framework import viewsets
from .serializers import NotificationSerializer
from .models import Notification
from rest_framework import permissions

# Create your views here.
class NotificationView(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
