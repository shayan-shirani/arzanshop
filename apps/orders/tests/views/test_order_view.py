from django.urls import reverse

import pytest
from unittest.mock import patch

from apps.orders.tests.factories import OrderItemFactory, OrderFactory
from apps.accounts.tests.factories import AddressFactory
from apps.orders.tests.conftest import api_client, user_factory, cart_session

@pytest.mark.django_db
def test_list_orders(api_client, user_factory):
    user = user_factory
    order = OrderFactory(buyer=user)
    api_client.force_authenticate(user=user)
    OrderItemFactory.create_batch(5, order=order)
    response = api_client.get(reverse('orders:orders-list'))
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
@patch('apps.orders.services.payment_services.PaymentService.pay_request')
def test_create_order(mocked_pay, api_client, user_factory, cart_session):
    user = user_factory
    address = AddressFactory(user=user)
    api_client.force_authenticate(user=user)
    data = {
        'address_id': address.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
    }
    mocked_pay.return_value = {'status': 'success', 'transaction_id': 'mocked-transaction-id'}
    response = api_client.post(reverse('orders:orders-list'), data=data)
    assert response.status_code == 201