from django.db import models
from django.contrib.auth.models import User

class Place(models.Model):
    name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

class Schedule(models.Model):
    money = models.PositiveIntegerField(null=False)
    memo = models.CharField(max_length=100, null=True)
    start_datetime = models.DateTimeField(null=True)
    end_datetime = models.DateTimeField(null=True)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)

class Travel(models.Model):
    title = models.CharField(max_length=50, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    travels = models.ManyToManyField(Travel)
    friends = models.ManyToManyField("Profile", blank=True)
    photo = models.ImageField(blank=True, null=True)

    def get_connections(self):
        connections = Connection.objects.filter(creator=self.user)
        return connections

    def get_followers(self):
        followers = Connection.objects.filter(following=self.user)
        return followers

class Review(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post_datetime = models.DateTimeField(null = True)
    post_title = models.CharField(max_length=100, null=True)
    post = models.CharField(max_length=100, null=True)
    photo = models.ImageField(blank=True, null=True)

class Notification(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    datetime = models.DateTimeField(null = True)
    title = models.CharField(max_length=100, null=True)
    content = models.CharField(max_length=100, null=True)

class Connection(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User, related_name="friendship_creator_set", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="friend_set", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
