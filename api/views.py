from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from rest_framework import status, viewsets, filters, permissions, exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from api.permissions import IsAdmin, IsAdminOrReadOnly
from api.serializers import UserSerializer, CategorySerializer
from users.models import User
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from api.models import Categories, Genres, Titles


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin, ]
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'


@api_view(['GET', 'PATCH'], )
@permission_classes([IsAuthenticated, ])
def view_self(request):
    user = User.objects.get(username=request.user.username)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    if request.method == 'PATCH':
        print(request.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_200_OK)


@api_view(['POST', ])
def signup(request):
    email = request.POST['email']
    if not User.objects.filter(email=email).exists():
        username = email.split('@')[0]
        user = User.objects.create(username=username, email=email)
    else:
        user = User.objects.filter(email=email).first()
    code = default_token_generator.make_token(user)
    mail.send_mail(
        subject='Your YaMDb confirmation code',
        message=f'"confirmation_code": "{code}"',
        from_email='admin@yamdb.com',
        recipient_list=[email, ],
        fail_silently=True
    )
    print(code)
    return Response(data={'email': email}, status=status.HTTP_200_OK)


@api_view(['POST', ])
def login(request):
    email = request.POST['email']
    confirmation_code = request.POST['confirmation_code']
    user = User.objects.filter(email=email).first()
    data = {'field_name': []}
    if user is None:
        data['field_name'].append('email')
    if not default_token_generator.check_token(user, confirmation_code):
        data['field_name'].append('confirmation_code')
    if len(data['field_name']) != 0:
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    token = RefreshToken.for_user(user)
    return Response(data={'token': str(token.access_token)}, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed('GET')
