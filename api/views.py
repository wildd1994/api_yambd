from django.shortcuts import render
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from api.serializers import CategorySerializer
from api.models import Categories, Genres, Titles
from api.permissions import IsAdminOrReadOnly
# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
    http_method_names = ['get', 'post', 'delete']
    lookup_field = 'slug'

    # def get_permissions(self):
    #     if self.action == 'list':
    #         permission_classes = [permissions.AllowAny]
    #     else:
    #         permission_classes = [IsAdmin]
    #     return [permission() for permission in permission_classes]
