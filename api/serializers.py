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
    # def validate(self, value):
    #     category = self.context['request']
    #     print(category.data)
    #     return value

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


class GenreField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class CategoryField(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class TitleSerializer(serializers.ModelSerializer):
    category = CategoryField(slug_field='slug', queryset=Categories.objects.all(), required=False)
    genre = GenreField(slug_field='slug', many=True, queryset=Genres.objects.all(), required=False)

    class Meta:
        model = Titles
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')

