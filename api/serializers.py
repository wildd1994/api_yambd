from django.shortcuts import get_object_or_404
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
    category = CategoryField(slug_field='slug',
                             queryset=Categories.objects.all(), required=False)
    genre = GenreField(slug_field='slug', many=True,
                       queryset=Genres.objects.all(), required=False)

    class Meta:
        model = Titles
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Titles, pk=title_id)
        if request.method == 'POST':
            if Reviews.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Author review already exists'
                )
        return data

    def create(self, validated_data):
        author = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Titles, pk=title_id)
        return Reviews.objects.create(
            title=title,
            author=author,
            **validated_data
        )

    class Meta:
        model = Reviews
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comments
        fields = '__all__'

    def create(self, validated_data):
        author = self.context['request'].user
        review_id = self.context['view'].kwargs.get('review_id')
        review = get_object_or_404(Reviews, pk=review_id)
        return Comments.objects.create(
            review=review,
            author=author,
            **validated_data
        )
