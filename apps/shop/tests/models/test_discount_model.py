import pytest

from apps.shop.tests.factories import DiscountFactory


@pytest.mark.django_db
def test_create_discount():
    discount = DiscountFactory()
    assert discount.is_active == True
    assert discount.start_date < discount.end_date

