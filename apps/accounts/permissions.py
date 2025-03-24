from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return True

        return user.is_authenticated and (user == obj or user.is_staff)