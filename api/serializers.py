from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model

from api.models import Categories, Genres, Titles, Reviews, Comments, YamDBUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализация пользователя
    Нельзя заводить пользователья с логином me.
    Оно пересекается с названием endpoint'а.
    Нельзя заводить имена с префикса, который использует робот
    при автоматическом создании имён логинов
    Добавлены новые поля bio, role
    """

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Запрещено использовать имя me')

        if value.startswith(User.AUTO_CREATE_USERNAME_PREFIX):
            raise serializers.ValidationError(
                (
                    'Имя не должно начинаться с '
                    f'{User.AUTO_CREATE_USERNAME_PREFIX}'
                )
            )
        return value

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role',
        )
        model = User


class RestrictedUserSerializer(UserSerializer):
    """
    Сериализация для POST, PATCH методов
    специальный сериализатор с ограничениями на изменение полей:
    нельзя менять роль
    """

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
        )
        model = User


class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailAuthTokenInputSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(required=True)


class EmailAuthTokenOutputSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        exclude = ('id',)


class TitleViewSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Titles
        fields = '__all__'


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Categories.objects.all(),
                                            required=False)
    genre = serializers.SlugRelatedField(slug_field='slug', many=True,
                                         queryset=Genres.objects.all(),
                                         required=False)

    class Meta:
        model = Titles
        fields = '__all__'


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
