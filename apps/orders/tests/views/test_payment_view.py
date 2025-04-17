import pytest
from unittest.mock import patch
from django.urls import reverse

from apps.orders.tests.factories import OrderFactory, SubscriptionFactory

@pytest.mark.django_db
@patch('apps.orders.services.payment_services.PaymentService.order_pay_verify')
def test_payment_callback_order_success(mock_verify, api_client):
    order = OrderFactory(transaction_id='test-transid')
    mock_verify.return_value = {'message': 'Payment successful'}
    url = reverse('orders:payment-callback') + '?type=order'
    data = {'transid': 'test-transid', 'status': '1'}
    response = api_client.post(url, data=data)
    assert response.status_code == 200
    assert response.data['message'] == 'Payment successful'
    mock_verify.assert_called_once_with(order, '1', 'test-transid')

@pytest.mark.django_db
@patch('apps.orders.services.payment_services.PaymentService.subscription_pay_verify')
def test_payment_callback_subscription_success(mock_verify, api_client):
    subscription = SubscriptionFactory(transaction_id='test-transid')
    mock_verify.return_value = {'message': 'Payment successful'}
    url = reverse('orders:payment-callback') + '?type=subscription'
    data = {'transid': 'test-transid', 'status': '1'}
    response = api_client.post(url, data=data)
    assert response.status_code == 200
    assert response.data['message'] == 'Payment successful'
    mock_verify.assert_called_once_with(subscription, '1', 'test-transid')

@pytest.mark.django_db
def test_payment_callback_invalid_type(api_client):
    url = reverse('orders:payment-callback') + '?type=invalid'
    data = {'transid': 'anything', 'status': '1'}
    response = api_client.post(url, data=data)
    assert response.status_code == 400
    assert response.data['error'] == 'Invalid payment type'

@pytest.mark.django_db
def test_payment_callback_order_not_found(api_client):
    url = reverse('orders:payment-callback') + '?type=order'
    data = {'transid': 'nonexistent', 'status': '1'}
    response = api_client.post(url, data=data)
    assert response.status_code == 404
    assert response.data['error'] == 'Order not found'

@pytest.mark.django_db
def test_payment_callback_subscription_not_found(api_client):
    url = reverse('orders:payment-callback') + '?type=subscription'
    data = {'transid': 'nonexistent', 'status': '1'}
    response = api_client.post(url, data=data)
    assert response.status_code == 404
    assert response.data['error'] == 'Subscription not found'
