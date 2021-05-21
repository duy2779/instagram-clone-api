from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # delete not use fields
    first_name = None
    last_name = None

    avatar_pic = models.ImageField(
        blank=True, null=True, default="default.png")
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=200)
    followers = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="following")
