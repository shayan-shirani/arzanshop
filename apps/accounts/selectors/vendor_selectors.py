from apps.accounts.models import VendorProfile

def get_all_vendors():
    return VendorProfile.objects.all()

def get_vendor_by_user(user):
    return VendorProfile.objects.filter(user=user)

def get_vendor_by_pk_status(pk, status):
    return VendorProfile.objects.get(pk=pk, status=status)