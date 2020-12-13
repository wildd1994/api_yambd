from rest_framework import serializers, validators
from rest_framework.validators import UniqueTogetherValidator

from users.models import User
from api.models import Categories, Genres, Titles, Reviews, Comments


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'bio', 'email',
                  'role', ]
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

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )
    title = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='description'
    )

    def validate(self, attrs):
        author = self.context['request'].user
        title = self.context['view'].kwargs.get('title_id')
        message = 'Author review already exists'
        if Reviews.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(message)
        return attrs

    class Meta:
        fields = '__all__'
        model = Reviews
        unique_together = ['author', 'title']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    post = serializers.SlugRelatedField(
        many=False,
        queryset=Reviews.objects.all(),
        slug_field='id',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Comments
        validators = [
            UniqueTogetherValidator(
                message='Comment already exists!',
                queryset=Comments.objects.all(),
                fields=['author', 'post']
            )
        ]

