from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, MinValueValidator, \
    MaxValueValidator
from django.db import models
from django.utils.deconstruct import deconstructible

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
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='categories')
    genres = models.ManyToManyField(Genres)


class Reviews(models.Model):
    text = models.TextField(blank=False, max_length=5000)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user'
    )
    score = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)]
    )
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name='title',
        null=True
    )

    def __str__(self):
        return f'{self.author} - {self.title}'

    class Meta:
        unique_together = ['author', 'title']


def validate_comment(value):
    if value == '':
        raise ValidationError(u'%s Комментарий не должен быть пустым' % value)


@deconstructible
class MaxValueValidator(BaseValidator):
    message = 'Ensure this value is less than or equal to %(limit_value)s.'
    code = 'max_value'

    def compare(self, a, b):
        return a > b


@deconstructible
class MinValueValidator(BaseValidator):
    message = 'Ensure this value is greater than or equal to %(limit_value)s.'
    code = 'min_value'

    def compare(self, a, b):
        return a < b


class Comments(models.Model):
    title_id = models.ForeignKey(
        Titles, on_delete=models.CASCADE,
        related_name='title_comment'
    )
    review_id = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name='comment',
        validators=[validate_comment]
    )
