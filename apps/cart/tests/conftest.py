import pytest

from apps.shop.tests.factories import ProductFactory, DiscountFactory
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def discount_factory():
    return DiscountFactory()

@pytest.fixture
def products_data():
    product = ProductFactory()
    second_product = ProductFactory()
    return product, second_product