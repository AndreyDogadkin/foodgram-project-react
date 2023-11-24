from django.core.handlers.wsgi import WSGIRequest
from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request: WSGIRequest, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)
