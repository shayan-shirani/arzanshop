from rest_framework.test import APIRequestFactory

import pytest

from apps.accounts.tests.factories import ShopUserFactory, AddressFactory, VendorProfileFactory

@pytest.fixture
def api_factory():
    return APIRequestFactory()

@pytest.fixture
def user_factory():
    return ShopUserFactory()

@pytest.fixture
def address_factory():
    return AddressFactory()

@pytest.fixture
def vendor_factory():
    return VendorProfileFactory()

@pytest.fixture
def validate_vendor():
    vendor_data = {
        'status': 'pending',
        'store_name': 'Test Store',
        'is_active': False,
    }
    return vendor_data

@pytest.fixture
def validate_user():
    user_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'johndoe',
        'phone': '12345678901',
        'email': 'johndoe@example.com',
        'password': 'securepassword123',
    }
    return user_data

@pytest.fixture
def validate_address():
    address_data = {
        'street': '123 Main St',
        'state': 'CA',
        'city': 'San Francisco',
        'zip_code': '94105',
        'country': 'USA',
    }
    return address_data