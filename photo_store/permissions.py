from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser or request.method in permissions.SAFE_METHODS:
            return True
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='Client').exists() and request.method == 'POST' or request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.owner


