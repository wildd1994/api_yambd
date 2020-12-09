from django.urls import include, path
from users.urls import users_router
from .views import view_self

urlpatterns = [
    path('v1/auth/', include('users.urls')),
    path('v1/users/me/', view_self),
    path('v1/users/', include(users_router.urls))
]
