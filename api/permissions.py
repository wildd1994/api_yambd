from rest_framework import permissions
from django.contrib.auth import get_user_model
#TODO Есть ощущения, что вы используете не все пермишены)
User = get_user_model()


class AdminOnly(permissions.BasePermission):
    #TODO Давайте этот пермишен тоже назовем единообразно
    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Only superuser and admin are allowed to use unsafe methods.
    """

    def has_permission(self, request, view):
        return (
            request.method == 'GET' or
            #TODO Давайте использовать список безопасных методов, их несколько
            (request.user.is_authenticated and request.user.is_admin)
            #TODO Здесь скобки тоже не нужны
        )


class IsUserOrModerator(permissions.BasePermission):
    """
    Only the author and moderator are allowed to use unsafe methods.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            obj.author == request.user or
            (request.method == 'DELETE' and request.user.is_moderator)
            #TODO Получается, модератор может только удалять? Это ок?Скобки не нужны=)
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
