from django.urls import path, include
from users.urls import users_router
from rest_framework import routers
from api.views import CategoryViewSet

router_api_v1 = routers.DefaultRouter()
router_api_v1.register('categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('v1/auth/', include('users.urls')),
    path('v1/users/', include(users_router.urls)),
    path('v1/', include(router_api_v1.urls)),
]
