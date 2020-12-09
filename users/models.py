from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if username is None:
            username = email.split('@')[0]

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.save(using=self._db)
        return user

    def create_staffuser(self, email, username=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if username is None:
            username = email.split('@')[0]

        user = self.create_user(
            email,
            username=username,
        )
        user.role = 'moderator'
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if username is None:
            username = email.split('@')[0]
        user = self.create_user(
            email,
            username=username,
        )
        user.role = 'admin'
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=100, null=False, blank=False, unique=True)
    email = models.EmailField(unique=True, blank=False)
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
    REQUIRED_FIELDS = ['email', ]
    objects = UserManager()
