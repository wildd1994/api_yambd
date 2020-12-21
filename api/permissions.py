from rest_framework import permissions
from django.contrib.auth import get_user_model
User = get_user_model()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin
        #TODO Я предлагал добавить проверку на авторизацию именно сюда, тогда бы во вьюхах было бы чуть лаконичнее)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Only superuser and admin are allowed to use unsafe methods.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or
            request.user.is_authenticated and request.user.is_admin
        )


class ReviewCommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or
                obj.author == request.user or
                request.user.role in ['admin', 'moderator'])
