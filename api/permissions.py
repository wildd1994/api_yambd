from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Только superuser и admin разрешено использовать небезопасные методы.
    """

    def has_permission(self, request, view):
        return (
            request.method == 'GET' or
            (request.user.is_authenticated and request.user.is_admin)
        )


class IsUserOrModerator(permissions.BasePermission):
    """
    Только автору и модератору разрешено использовать небезопасные методы.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            obj.author == request.user or
            (request.method == 'DELETE' and request.user.is_moderator)
        )


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'admin'


class IsModerator(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'moderator'


class IsAuthorOrReadonly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or
                request.user.role == 'admin')


class ReviewCommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or
                obj.author == request.user or
                request.user.role in ['admin', 'moderator'])
