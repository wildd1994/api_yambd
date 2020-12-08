from rest_framework import permissions


class IsAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin'
