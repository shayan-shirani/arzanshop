from apps.orders.models import Subscription

def get_all_subscription():
    return Subscription.objects.all()

def get_subscription_by_user(user):
    return Subscription.objects.get(user=user)