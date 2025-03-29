from apps.orders.models import Subscription

def get_all_subscription():
    return Subscription.objects.all()