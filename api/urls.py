from django.urls import include, path
from users.urls import users_router
from rest_framework import routers
from api.views import CategoryViewSet, view_self, GenresViewSet, TitleViewSet

router_api_v1 = routers.DefaultRouter()
router_api_v1.register('categories', CategoryViewSet, basename='categories')
router_api_v1.register('genres', GenresViewSet, basename='genres')
router_api_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/auth/', include('users.urls')),
    path('v1/users/me/', view_self),
    path('v1/users/', include(users_router.urls)),
    path('v1/', include(router_api_v1.urls)),
]
