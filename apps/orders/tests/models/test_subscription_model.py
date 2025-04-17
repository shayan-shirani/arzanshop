from django.utils import timezone

import pytest
from datetime import timedelta

from apps.orders.models import Subscription
from apps.orders.tests.factories import SubscriptionFactory

@pytest.mark.django_db
def test_subscription_creation():
    subscription = SubscriptionFactory()
    assert subscription.buyer is not None
    assert subscription.plan == Subscription.PlanType.MONTHLY
    assert subscription.price == Subscription.PlanPrice.MONTHLY
    assert subscription.is_active
    assert subscription.paid
    assert subscription.start_date <= timezone.now()
    assert subscription.end_date == subscription.start_date + timedelta(days=30)

@pytest.mark.django_db
def test_subscription_is_valid_active():
    subscription = SubscriptionFactory()
    assert subscription.is_valid() is True

@pytest.mark.django_db
def test_subscription_is_valid_inactive():
    subscription = SubscriptionFactory(is_active=False)
    assert subscription.is_valid() is False

@pytest.mark.django_db
def test_subscription_discount_monthly():
    subscription = SubscriptionFactory(plan=Subscription.PlanType.MONTHLY)
    assert subscription.discount() == 10

@pytest.mark.django_db
def test_subscription_discount_yearly():
    subscription = SubscriptionFactory(plan=Subscription.PlanType.YEARLY)
    subscription.end_date = subscription.start_date + timedelta(days=365)
    subscription.price = Subscription.PlanPrice.YEARLY
    subscription.save()
    assert subscription.discount() == 20