from django.contrib.auth import get_user_model
from django.db import models

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
    year = models.IntegerField(null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True,
                                 related_name='categories')
    genre = models.ManyToManyField(Genres)
    rating = models.IntegerField(default=None, null=True)
    description = models.TextField(max_length=2000, default='')
