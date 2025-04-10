from rest_framework.permissions import BasePermission

from apps.accounts.models import VendorProfile

class IsUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, VendorProfile):
            return user.is_authenticated and (user == obj.user or user.is_staff)

        return user.is_authenticated and (user == obj or user.is_staff)