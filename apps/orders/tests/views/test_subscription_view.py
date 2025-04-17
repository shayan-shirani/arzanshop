from django.urls import reverse

import pytest
from unittest.mock import patch

from apps.orders.tests.factories import SubscriptionFactory
from apps.orders.tests.conftest import api_client, user_factory


@pytest.mark.django_db
def test_list_subscriptions(api_client, user_factory):
    user = user_factory
    SubscriptionFactory.create(buyer=user)
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse('orders:subscriptions-list'))
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
@patch('apps.orders.services.payment_services.PaymentService.pay_request')
def test_create_subscription(mocked_pay, api_client, user_factory, cart_session):
    user = user_factory
    data = {
        'subscription_plan': 'monthly'
    }
    api_client.force_authenticate(user=user)
    mocked_pay.return_value = {'status': 'success', 'transaction_id': 'mocked-transaction-id'}
    response = api_client.post(reverse('orders:subscriptions-list'), data)
    assert response.status_code == 201