from django.urls import path, include
from users.urls import users_router

urlpatterns = [
    path('v1/auth/', include('users.urls')),
    path('v1/users/', include(users_router.urls))
]
