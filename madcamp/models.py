from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    spouse_name = models.CharField(blank=True, max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.email


class Place(models.Model):
    name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    #latitude = models.FloatField()
    #longitude = models.FloatField()

class Travel(models.Model):
    title = models.CharField(max_length=50, null=True)
    place_name = models.CharField(max_length=50, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField("Profile")

class Schedule(models.Model):
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE, null = True)
    day = models.PositiveIntegerField(null=False, default=1)
    money = models.PositiveIntegerField(null=False)
    memo = models.CharField(max_length=100, null=True)
    start_datetime = models.TimeField(null=True)
    end_datetime = models.TimeField(null=True)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    travels = models.ManyToManyField("Travel", related_name="travels_set", blank=True)
    friends = models.ManyToManyField("Profile", related_name="friends_set", blank=True)
    pending_requests = models.ManyToManyField("Profile", related_name="pending_set", blank=True)
    pending_travels = models.ManyToManyField("Travel", related_name="pending_travels_set", blank=True)
    photo = models.CharField(blank=True, null=True, max_length=100)

class Review(models.Model):
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE, null = True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post_datetime = models.DateTimeField(null = True)
    post_title = models.CharField(max_length=100, null=True)
    post = models.CharField(max_length=100, null=True)
    photo = models.ImageField(blank=True, null=True)

class Notification(models.Model):
    # creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # datetime = models.DateTimeField(null = True)
    title = models.CharField(max_length=100, null=True)
    content = models.CharField(max_length=100, null=True)