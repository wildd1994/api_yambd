from rest_framework import permissions


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


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.role == 'admin'

        return False


class ReviewCommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS or
                obj.author == request.user or
                request.user.is_moderator or
                request.user.is_admin)
