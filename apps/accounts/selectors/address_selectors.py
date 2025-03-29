from apps.accounts.models import Addresses

def get_all_addresses():
    return Addresses.objects.all()

def get_address_by_user(user):
    return Addresses.objects.filter(user=user)

def get_address_by_id(id):
    return Addresses.objects.get(id=id)