from django.db import IntegrityError

import pytest

from apps.accounts.tests.factories import VendorProfileFactory
from apps.shop.tests.factories import (
    CategoryFactory,
    ProductFactory,
)

@pytest.mark.django_db
def test_create_product():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    product = ProductFactory(category=category, vendor=vendor)
    assert product.category == category
    assert product.vendor == vendor

@pytest.mark.django_db
def test_create_product_without_vendor_or_category():
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(vendor=None, category=None)
    assert 'violates not-null constraint' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_create_product_with_invalid_price():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(price=-1, category=category, vendor=vendor)
    assert 'shop_product_price_check' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_create_product_with_invalid_stock():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(stock=-1, category=category, vendor=vendor)
    assert 'shop_product_stock_check' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_create_product_with_invalid_weight():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(weight=-1, category=category, vendor=vendor)
    assert 'shop_product_weight_check' in str(excinfo.value).lower()