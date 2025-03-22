from rest_framework import permissions
from accounts.models import ShopUser, VendorProfile
class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
       user = request.user
       if user.is_authenticated and user.role == ShopUser.Roles.VENDOR and hasattr(user, 'vendor_profile'):
           return user.vendor_profile.status == VendorProfile.Status.APPROVED
       return False