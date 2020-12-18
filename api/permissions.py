from rest_framework import permissions
from django.contrib.auth import get_user_model
#TODO Есть ощущения, что вы используете не все пермишены)
User = get_user_model()

#Предлагаю название IsAdministrator . Что думаете?
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
            request.method in permissions.SAFE_METHODS or
            request.user.is_authenticated and request.user.is_admin
        )


class IsUserOrModerator(permissions.BasePermission):
    """
    Only the author and moderator are allowed to use unsafe methods.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            obj.author == request.user or
            request.method == ['DELETE', 'PUT'] and request.user.is_moderator
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
