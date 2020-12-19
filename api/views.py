from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from api.permissions import \
    ReviewCommentPermission
from api.serializers import CategorySerializer, \
    GenreSerializer, TitlePostSerializer, TitleViewSerializer, \
    ReviewSerializer, CommentSerializer
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


def _get_token_for_user(user):
#TODO Это очень похоже на функцию однострочник, которая используется только в одном месте. Можно обойтись и без нее
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class UsersViewSet(viewsets.ModelViewSet):
    """
    Filter on is_active: users must first pass activation
    via e-mail before they get access to the social network.
    #TODO А мне кажется, что в апи должны присутствовать все пользователи, независимо от активации. Тем более для админа
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin)
    #TODO Не хватит ли тут одного пермишена?
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
            return response.Response(serializer.data)
            #TODO (не обязательно) Давайте для ясности везде явно возвращать статусы

        serializer = RestrictedUserSerializer(
            user_object,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #TODO Как раз, пользователь не должен уметь изменить свою роль, так как это не безопасно
        return response.Response(serializer.data)


@decorators.api_view(['POST'])
def auth_send_email(request):
    """
    The first part of the user creation algorithm.
    an inactive user is being created.
    The user is sent a confirmation code to the specified e-mail address.
    also this endpoint can be used for repeated receiving
    the confirmation code. in this case, the user's status does not change.
    """
    input_data = EmailAuthSerializer(data=request.data)
    input_data.is_valid(raise_exception=True)
    email = input_data.validated_data['email']

    user_object, created = User.objects.get_or_create(email=email)
    #TODO Давайте наравне пользоваться ником, коль уж он передается

    if created:
        user_object.is_active = False
        #TODO Получается, если пользователь потерял письмо с токеном, то всё, он больше не сможет получить доступ? Только создавать нового с новой почты? Кажется, не очень правильным поведением.
        user_object.save()

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
        user_object.is_active = True
        user_object.save()

    token = _get_token_for_user(user_object)

    output_data = EmailAuthTokenOutputSerializer(data={'token': token})
    output_data.is_valid()
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
    queryset = Titles.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
        #TODO (не обязательно) Можно воспользоваться in
            return TitleViewSerializer
        return TitlePostSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.rating = instance.reviews.all().aggregate(Avg('score'))[
        #TODO Давайте не будем переопределять целый метод лучше задать аннотацию в кверисете в атрибутах класса
            'score__avg']
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewCommentPermission]
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        title = get_object_or_404(Titles, id=self.kwargs.get('title_id'))
        if Reviews.objects.filter(
        #TODO Это валидация, ее нужно убрать в сериализатор
                author=self.request.user,
                title=title
        ).exists():
            raise ValidationError('Оценка уже выставлена')
        serializer.save(author=self.request.user, title=title)
        agg_score = Reviews.objects.filter(title=title).aggregate(Avg('score'))
        title.rating = agg_score['score__avg']
        #TODO Опять же, рейтинг должен считаться "на лету", а не храниться в базе
        title.save(update_fields=['rating'])

    def perform_update(self, serializer):
        serializer.save()
        title = get_object_or_404(Titles, pk=self.kwargs.get('title_id'))
        agg_score = Reviews.objects.filter(title=title).aggregate(Avg('score'))
        title.rating = agg_score['score__avg']
        title.save(update_fields=['rating'])

    def get_queryset(self):
        title = get_object_or_404(Titles, pk=self.kwargs.get('title_id'))
        return Reviews.objects.filter(title=title)


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
