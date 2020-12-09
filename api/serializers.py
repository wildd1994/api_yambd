from rest_framework import serializers, validators
from users.models import User
from api.models import Categories, Genres, Titles


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'email', 'role', ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'bio': {'required': False},
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name', 'slug')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Categories.objects.all(),
                fields=['slug'],
                message='Нельзя создать существующую категорию',
            )
        ]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ('name', 'slug')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Genres.objects.all(),
                fields=['slug'],
                message='Нельзя создать существующий жанр',
            )
        ]


class TitleSerializer(serializers.ModelSerializer):
    pass
