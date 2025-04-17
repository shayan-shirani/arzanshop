import pytest

from apps.accounts.tests.factories import AddressFactory, ShopUserFactory
from apps.orders.tests.factories import OrderFactory

@pytest.mark.django_db
def test_create_order():
    address = AddressFactory()
    buyer = ShopUserFactory()
    order = OrderFactory(buyer=buyer, address=address)
    assert order.address == address
    assert order.buyer == buyer
    assert order.first_name
    assert order.last_name
    assert order.transaction_id
    assert order.paid == False
