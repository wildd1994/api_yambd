from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


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
    slug = models.SlugField(max_length=150)
    year = models.IntegerField()
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True, related_name='categories')
    genres = models.ManyToManyField(Genres)
