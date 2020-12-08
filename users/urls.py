from users import views
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserViewSet

users_router = SimpleRouter()
users_router.register('', UserViewSet, basename='users')
users_router.register(
    r'(?P<username>\d+)/',
    UserViewSet,
    basename='user'
)

urlpatterns = [
    path('email/', views.signup, name='signup'),
    path('token/', views.login, name='login'),
]
