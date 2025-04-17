import pytest

from apps.orders.tests.factories import OrderFactory, OrderItemFactory
from apps.shop.tests.factories import CategoryFactory, ProductFactory

@pytest.mark.django_db
def test_create_order_item():
    category = CategoryFactory()
    product = ProductFactory(category=category)
    order = OrderFactory()
    order_item = OrderItemFactory(product=product, order=order)
    assert order_item.product == product
    assert order_item.order == order
    assert order_item.quantity
    assert order_item.price