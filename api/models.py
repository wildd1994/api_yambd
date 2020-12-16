from django.contrib.auth import get_user_model
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
#  from api.models import


class Role(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class YamDBUser(AbstractUser):
    AUTO_CREATE_USERNAME_PREFIX = 'yamdb_user'
    email = models.EmailField(unique=True, blank=False, verbose_name='Электронная почта')
    bio = models.TextField(blank=True, max_length=1000)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

    @property
    def is_admin(self):
        return self.is_superuser or (self.role == Role.ADMIN)

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR


class Categories(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=150)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=150)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='categories')
    genre = models.ManyToManyField(Genres)
    rating = models.IntegerField(default=None, null=True)
    description = models.TextField(max_length=2000, default='')


class Reviews(models.Model):
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(blank=False, max_length=5000)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        YamDBUser,
        on_delete=models.CASCADE,
        related_name='user'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)]
    )

    class Meta:
        ordering = ['-pub_date']


class Comments(models.Model):
    review = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        verbose_name='commented review',
        related_name='comments'
    )
    text = models.TextField(
        'comment text',
        blank=False,
        help_text='Напишите ваш комментарий'
    )
    author = models.ForeignKey(
        YamDBUser,
        on_delete=models.CASCADE,
        verbose_name='commented author',
        related_name='comments'
    )
    pub_date = models.DateTimeField('comment date', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
