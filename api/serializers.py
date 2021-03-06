from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.models import Categories, Genres, Titles, Reviews, Comments, YamDBUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
    username = serializers.CharField()


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
    rating = serializers.FloatField(read_only=True)

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

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data

        title_id = self.context.get('view').kwargs.get('title_id')
        user = self.context.get('request').user
        queryset = Reviews.objects.filter(author=user, title=title_id)
        if queryset.exists():
            raise serializers.ValidationError(
                'Можно оставить только один отзыв на произведение.'
            )
        return data


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
