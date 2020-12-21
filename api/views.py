from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from api.permissions import \
    ReviewCommentPermission
from api.serializers import CategorySerializer, \
    GenreSerializer, TitlePostSerializer, TitleViewSerializer, \
    ReviewSerializer, CommentSerializer, EmailSerializer
from api.models import *
from api.filters import CustomFilter
from smtplib import SMTPException
from django.contrib.auth.tokens import default_token_generator

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (decorators, filters, mixins, permissions, response,
                            status, viewsets)
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdmin, IsAdminOrReadOnly
from .serializers import (EmailAuthSerializer,
                          EmailAuthTokenInputSerializer,
                          EmailAuthTokenOutputSerializer,
                          RestrictedUserSerializer,
                          UserSerializer)

User = get_user_model()

token_generator = PasswordResetTokenGenerator()


class UsersViewSet(viewsets.ModelViewSet):
    """
    Working with users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @decorators.action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """
        Which gives and edits
        information for the profile of the current authorized user.
        """
        user_object = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            serializer = UserSerializer(user_object)
            return response.Response(serializer.data,
                                     status=status.HTTP_200_OK)

        serializer = RestrictedUserSerializer(
            user_object,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(['POST'])
def auth_send_email(request):
    """
    The first part of the user creation algorithm.
    an inactive user is being created.
    The user is sent a confirmation code to the specified e-mail address.
    also this endpoint can be used for repeated receiving
    the confirmation code. in this case, the user's status does not change.
    """
    serializer = EmailSerializer(data=request.data)
    #TODO Давайте просто добавим в один сериализатор ник и в этой вьюхе будем пользоваться только им
    serializer.is_valid(raise_exception=True)
    input_data = EmailAuthSerializer(data=request.data)
    input_data.is_valid(raise_exception=True)
    email = input_data.validated_data['email']
    username = serializer.data.get('username')

    user_object, created = User.objects.get_or_create(email=email,
                                                      username=username)

    confirmation_code = default_token_generator.make_token(user_object)

    try:
        send_mail(
            'Getting access to the yamdb social network',
            f'Your activation code: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except SMTPException as e:
        return response.Response(
            f'Error sending e-mail: {e}',
            status=status.HTTP_400_BAD_REQUEST
        )

    return response.Response(input_data.data, status=status.HTTP_200_OK)


@decorators.api_view(['POST'])
def auth_get_token(request):
    """
    The second part of the user creation algorithm.
    By e-mail and confirmation code, the user receives a token to
    work in the system. So his account is activated.
    This endpoint can also be used to get the token again.
    """
    input_data = EmailAuthTokenInputSerializer(data=request.data)
    input_data.is_valid(raise_exception=True)
    email = input_data.validated_data['email']
    confirmation_code = input_data.validated_data['confirmation_code']

    user_object = get_object_or_404(User, email=email)

    if not token_generator.check_token(user_object, confirmation_code):
        return response.Response(
            'Неверный код подтверждения',
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user_object.is_active:
    #TODO Лишняя логика осталась)
        user_object.is_active = True
        user_object.save()

    token = RefreshToken.for_user(user_object)

    output_data = EmailAuthTokenOutputSerializer(data={'token': token})
    output_data.is_valid()
    #TODO Так как это ваши данные, то их не нужно проверять на валидность)
    return response.Response(output_data.data, status=status.HTTP_200_OK)


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """
    A viewset that provides `destroy`, `create`, and `list` actions.
    """
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    lookup_field = 'slug'


class GenresViewSet(ListCreateDestroyViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomFilter

    def get_serializer_class(self):
        if 'list' in self.action or 'retrieve' in self.action:
            return TitleViewSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewCommentPermission]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Titles, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Titles, id=title_id)
        serializer.save(author=self.request.user, title_id=title.id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [ReviewCommentPermission]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(Reviews, pk=self.kwargs.get('review_id'))
        return Comments.objects.filter(review=review)

    def perform_create(self, serializer):
        review = get_object_or_404(Reviews, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
