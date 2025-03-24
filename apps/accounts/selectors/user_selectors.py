from apps.accounts.models import ShopUser

def get_all_users():
    return ShopUser.objects.all()

def get_user_by_id(user_id):
    return ShopUser.objects.get(id=user_id)