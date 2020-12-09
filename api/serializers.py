from rest_framework import serializers, validators
from api.models import Categories, Genres, Titles


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
    pass


class TitleSerializer(serializers.ModelSerializer):
    pass