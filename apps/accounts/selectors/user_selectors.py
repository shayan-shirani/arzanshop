from django.utils.http import urlsafe_base64_decode

from apps.accounts.models import ShopUser

def get_all_users():
    return ShopUser.objects.all()

def get_user_by_id(user_id):
    return ShopUser.objects.get(id=user_id)

def get_user_by_email(username):
    return ShopUser.objects.get(email=username)

def get_user_by_phone(username):
    return ShopUser.objects.get(phone=username)

def get_user_by_uidb64(uidb64):
        uid = urlsafe_base64_decode(uidb64).decode()
        return ShopUser.objects.get(pk=uid)