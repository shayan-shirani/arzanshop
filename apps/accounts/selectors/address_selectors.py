from apps.accounts.models import Addresses

def get_all_addresses():
    return Addresses.objects.all()

def filter_address_by_user(user):
    return Addresses.objects.filter(user=user)

def get_address_by_id(address_id):
    return Addresses.objects.get(id=address_id)