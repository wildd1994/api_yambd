from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class User(AbstractBaseUser):
    username = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=1000)
    role = models.CharField(
        max_length=10,
        choices=[
            ('user', 'user'),
            ('moderator', 'moderator'),
            ('admin', 'admin'),
        ],
        default='user'
    )

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
