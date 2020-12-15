from django.db import models
from django.contrib.auth.models import AbstractUser  # , BaseUserManager


class UserRoles(models.TextChoices):
    """Possible user roles"""
    USR = 'user', ('User')
    MOD = 'moderator', ('Moderator')
    ADM = 'admin', ('Admin')


class User(AbstractUser):
    username = models.CharField(max_length=100, null=False, blank=False, unique=True)
    email = models.EmailField(unique=True, blank=False, verbose_name='Электронная почта')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=1000)
    role = models.CharField(
        max_length=20,
        choices=UserRoles.choices,
        default=UserRoles.USR,
        verbose_name='Роль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    # @property
    # def is_moderator(self):
    # return self.role == self.UserRoles.MOD

    # @property
    # def is_admin(self):
    # return self.role == self.UserRoles.ADM
