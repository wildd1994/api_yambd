from django.shortcuts import render, get_object_or_404
from django.core import mail
from django.utils.crypto import get_random_string
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin, ]
    http_method_names = ['get', 'post', 'patch', 'delete']


@api_view(['POST', ])
def signup(request):
    user, new_user = User.objects.get_or_create(
        email=request.POST['email'],
        defaults={
            'username': request.POST['email'],
            'role': 'user'
        }
    )
    code = get_random_string(length=32)
    mail.send_mail(
        subject='Your YaMDb confirmation code',
        message=f'"confirmation_code": "{code}"',
        from_email='admin@yamdb.com',
        recipient_list=[user.email, ],
        fail_silently=True
    )
    print(code)
    return Response(data={'email': user.email}, status=status.HTTP_200_OK)


@api_view(['POST', ])
def login(request):
    email = request.POST['email']
    confirmation_code = request.POST['confirmation_code']
    if email is not None and confirmation_code is not None:
        user = get_object_or_404(User, email=email)
        print(user)
        token, created = Token.objects.get_or_create(user=user)
        return Response(data={'token': token}, status=status.HTTP_200_OK)
