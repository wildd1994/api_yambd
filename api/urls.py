from django.urls import include, path
from rest_framework import routers
from api.views import *

router_api_v1 = routers.DefaultRouter()
router_api_v1.register('users', UsersViewSet)
router_api_v1.register('categories', CategoryViewSet, basename='categories')
router_api_v1.register('genres', GenresViewSet, basename='genres')
router_api_v1.register('titles', TitleViewSet, basename='titles')
router_api_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                       basename='reviews')
router_api_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')

auth_url_patterns = [
    path('email/', auth_send_email, name='auth_send_mail'),
    path('token/', auth_get_token, name='auth_get_token'),
]

v1_url_patterns = [
    path('', include(router_api_v1.urls)),
    path('auth/', include(auth_url_patterns)),
]

urlpatterns = [
    path('v1/', include(v1_url_patterns)),
]
