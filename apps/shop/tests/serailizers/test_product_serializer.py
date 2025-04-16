import pytest

from apps.shop.serializers import ProductCreateSerializer

from apps.accounts.tests.factories import VendorProfileFactory
from apps.shop.tests.factories import (
    ParentCategoryFactory,
    CategoryFactory,
)

from apps.shop.tests.conftest import api_factory, user_factory

@pytest.mark.django_db
def test_product_serializer_create(api_factory, user_factory):
    request = api_factory.post('/vendor-products/')
    request.user = user_factory
    root_category = ParentCategoryFactory()
    child_category = CategoryFactory(parent=root_category)
    vendor = VendorProfileFactory(user=request.user)
    product_data = {
        'vendor': vendor,
        'name': 'Test Product',
        'description': 'Test Description',
        'price': 1000,
        'stock': 10,
        'weight': 100,
        'category': child_category.id,
        'tags': ['example_tag'],
    }
    serializer = ProductCreateSerializer(data=product_data, context={'request': request})
    assert serializer.is_valid()
    product = serializer.save()
    assert product.vendor == vendor
    assert product.name == product_data['name']
    assert product.description == product_data['description']
    assert product.price == product_data['price']
    assert product.stock == product_data['stock']
    assert product.weight == product_data['weight']
    assert product.category == child_category