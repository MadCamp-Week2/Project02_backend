# api/urls.py
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import *

test_list = NotificationView.as_view({
    'post': 'create',
    'get': 'list'
})

urlpatterns = format_suffix_patterns([
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('test/', test_list, name='test_list'),
    path('signup/', views.createUser),
    path('login/', views.login),
    path('check/', views.checkUser),
    path('travels/', views.add_travel),
    path('travels/get/', views.get_travel)
])
