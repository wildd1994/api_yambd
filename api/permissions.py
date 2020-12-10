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


class OwnResourcePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or \
               obj.author == request.user or \
               request.method == 'DELETE' and IsAdmin


class IsAuthorOrIsStaffPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_authenticated and
            request.method in ('PATCH', 'DELETE') and (
                    request.user == obj.author or
                    request.user.role == 'admin' or
                    request.user.role == 'moderator' or
                    request.user.is_staff or
                    request.user.is_superuser
            )
        )
