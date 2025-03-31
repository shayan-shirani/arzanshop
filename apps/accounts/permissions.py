from rest_framework.permissions import BasePermission

class IsUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        return user.is_authenticated and (user == obj or user.is_staff)