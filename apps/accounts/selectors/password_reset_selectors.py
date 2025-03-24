from django.utils.http import urlsafe_base64_decode

from apps.accounts.models import ShopUser

def get_user_by_email(email):
    return ShopUser.objects.get(email=email)

def get_user_by_uidb64(uidb64):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        return ShopUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, ShopUser.DoesNotExist):
        raise ValueError("Invalid UID or user not found.")
