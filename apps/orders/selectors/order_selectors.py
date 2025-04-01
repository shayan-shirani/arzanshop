from apps.orders.models import Order


def get_all_orders():
    return Order.objects.all()

def filter_orders_by_user(user):
    return Order.objects.filter(user=user)