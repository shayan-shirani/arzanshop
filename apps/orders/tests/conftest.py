from rest_framework.test import APIClient

import pytest

from apps.accounts.tests.factories import ShopUserFactory
from apps.shop.tests.factories import ProductFactory
from apps.orders.tests.factories import (
    OrderFactory,
    OrderItemFactory,
    SubscriptionFactory
)


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_factory():
    return ShopUserFactory()

@pytest.fixture
def product_factory():
    return ProductFactory()

@pytest.fixture
def cart_session(api_client, product_factory):
    session = api_client.session
    product = product_factory
    session['cart'] = {
        str(product.id): {
            'quantity': 1,
            'price': product.price,
            'weight': product.weight,
        }
    }
    session.save()
    return session

@pytest.fixture
def order_item_factory():
    return OrderItemFactory()

@pytest.fixture
def order_factory():
    return OrderFactory()

@pytest.fixture
def subscription_factory():
    return SubscriptionFactory()