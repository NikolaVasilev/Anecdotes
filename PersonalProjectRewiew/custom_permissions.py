from rest_framework import permissions


class IsGetOrIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        return request.user and request.user.is_authenticated


class IsPostAndIsNotAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST' and (request.user.is_anonymous or request.user.is_staff):
            return True
        elif request.method == 'POST' and request.user.is_authenticated and request.user.is_staff is False:
            return False
        elif request.method != 'POST' and request.user.is_anonymous:
            return False

        return request.user and request.user.is_authenticated


class IsOwnerOrIsAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if (request.method == 'PUT' or request.method == 'DELETE') and (request.user.is_staff or request.user == (obj.created_by if hasattr(obj, 'created_by') else obj.user)):
            return True

        return False
