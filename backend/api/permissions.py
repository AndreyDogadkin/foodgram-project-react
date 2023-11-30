from rest_framework import permissions
from rest_framework.request import Request


class IsAuthorOrAdminOrHigherOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request: Request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.role != 'user')  # TODO Подумать над is_staff


class IsRequestUserOrAdminOrHigherOrReadonly(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user
                or request.user.role != 'user')
