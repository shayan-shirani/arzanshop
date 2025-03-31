from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.accounts.models import ShopUser, VendorProfile

class IsVendor(BasePermission):
    def has_permission(self, request, view):
       user = request.user

       if request.method in SAFE_METHODS:
           return True

       if user.is_authenticated and user.role == ShopUser.Roles.VENDOR and hasattr(user, 'vendor_profile'):
           return user.vendor_profile.status == VendorProfile.Status.APPROVED

       return False