from rest_framework.test import APIRequestFactory, APIClient

import pytest

from apps.accounts.models import ShopUser, VendorProfile

from apps.accounts.tests.factories import ShopUserFactory, VendorProfileFactory
from apps.shop.tests.factories import (
    ProductFactory,
    ParentCategoryFactory,
    CategoryFactory,
)


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def api_factory():
    return APIRequestFactory()

@pytest.fixture
def user_factory():
    return ShopUserFactory()

@pytest.fixture
def vendor_factory():
    return VendorProfileFactory()

@pytest.fixture
def product_factory():
    return ProductFactory()

@pytest.fixture
def approved_vendor_user():
    user = ShopUserFactory(role=ShopUser.Roles.VENDOR)
    VendorProfileFactory(user=user, status=VendorProfile.Status.APPROVED, is_active=True)
    return user

@pytest.fixture
def parent_category_factory():
    return ParentCategoryFactory()

@pytest.fixture
def child_category_factory(parent_category_factory):
    return CategoryFactory(parent=parent_category_factory)

@pytest.fixture
def validate_product(product_factory):
    vendor = product_factory.vendor
    category = product_factory.category.id
    product_data = {
        'vendor': vendor,
        'name': 'Test Product',
        'description': 'Test Description',
        'price': 1000,
        'stock': 10,
        'weight': 100,
        'category': category,
        'tags': ['example_tag'],
    }
    return product_data