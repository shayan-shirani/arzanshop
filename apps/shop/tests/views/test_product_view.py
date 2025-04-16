from  django.urls import reverse

from rest_framework import status

import pytest

from apps.shop.tests.conftest import (
    api_client,
    vendor_factory,
    validate_product,
    approved_vendor_user,
    child_category_factory
)
from apps.shop.tests.factories import ProductFactory

@pytest.mark.django_db
def test_product_list_authenticated_vendor(api_client, vendor_factory):
    user = vendor_factory
    api_client.force_authenticate(user=user)
    ProductFactory.create_batch(5)
    response = api_client.get(reverse('shop:vendor_products-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5

@pytest.mark.django_db
def test_product_list_unauthenticated(api_client):
    ProductFactory.create_batch(5)
    response = api_client.get(reverse('shop:vendor_products-list'))
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_create_product_success(api_client, validate_product, approved_vendor_user):
    user = approved_vendor_user
    api_client.force_authenticate(user=user)
    data = validate_product
    response = api_client.post(reverse('shop:vendor_products-list'), data=data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_product_forbidden_for_non_vendor(api_client, user_factory, child_category_factory):
    user = user_factory
    data = {
        'name': 'Test Product',
        'description': 'Test Description',
        'price': 1000,
        'stock': 10,
        'weight': 100,
        'category': child_category_factory,
        'tags': ['example_tag'],
    }
    api_client.force_authenticate(user=user)
    response = api_client.post(reverse('shop:vendor_products-list'), data=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_create_product_invalid_data(api_client, approved_vendor_user, child_category_factory):
    user = approved_vendor_user
    api_client.force_authenticate(user=user)
    data = {
        'description': 'Test Description',
        'price': 1000,
        'stock': 10,
        'weight': 100,
        'category': child_category_factory,
        'tags': ['example_tag'],
    }
    response = api_client.post(reverse('shop:vendor_products-list'), data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_update_product_success(api_client, approved_vendor_user):
    user = approved_vendor_user
    product = ProductFactory(vendor=user.vendor_profile)
    api_client.force_authenticate(user=user)
    data = {'name': 'Updated Product'}
    response = api_client.patch(reverse('shop:vendor_products-detail', args=[product.id]), data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Updated Product'

@pytest.mark.django_db
def test_delete_product_success(api_client, approved_vendor_user):
    user = approved_vendor_user
    product = ProductFactory(vendor=user.vendor_profile)
    api_client.force_authenticate(user=user)
    response = api_client.delete(reverse('shop:vendor_products-detail', args=[product.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
