from django_filters import rest_framework as filters
from api.models import Titles


class CustomFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='contains')
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')
    year = filters.NumberFilter(field_name='year')

    class Meta:
        model = Titles
        fields = ['category', 'genre', 'name', 'year']
