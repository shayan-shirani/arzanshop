from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VendorProfile, ShopUser

@receiver(post_save, sender=VendorProfile)
def vendor_profile_saved(sender, instance, **kwargs):
    if instance.is_active and instance.status != VendorProfile.STATUS.APPROVED:
        instance.status = VendorProfile.STATUS.APPROVED
        instance.user.role = ShopUser.Roles.VENDOR
        instance.user.save(update_fields=['role'])
        instance.save(update_fields=['status'])