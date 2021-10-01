from rest_framework import permissions


class AdminOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if (
            request.method in ['PUT', 'DELETE', 'PATCH'] and not user.is_anonymous
        ):
            return (
                user == obj.author or user.is_superuser
            )
        return request.method in permissions.SAFE_METHODS
