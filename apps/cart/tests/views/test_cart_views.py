from django.urls import reverse
from rest_framework import status

import pytest

from apps.cart.tests.conftest import (
    api_client,
    products_data,
    discount_factory
)


@pytest.mark.django_db
def test_cart_view(api_client, products_data, discount_factory):
    response = api_client.get(reverse('cart:cart-list'))
    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response.data


@pytest.mark.django_db
def test_add_product_to_cart(api_client, products_data):
    products = products_data
    product_id = {
        'product': products[0].id,
    }
    response = api_client.post(reverse('cart:cart-add'), product_id)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Product added'


@pytest.mark.django_db
def test_decrease_product_quantity(api_client, products_data):
    products = products_data
    product_id = {
        'product': products[0].id,
    }
    api_client.post(reverse('cart:cart-add'), product_id)
    response = api_client.post(reverse('cart:cart-decrease'), product_id)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Product decreased'


@pytest.mark.django_db
def test_remove_product_from_cart(api_client, products_data):
    products = products_data
    product_id = {
        'product': products[0].id,
    }
    api_client.post(reverse('cart:cart-add'), product_id)
    api_client.post(reverse('cart:cart-add'), product_id)
    response = api_client.post(reverse('cart:cart-remove'), product_id)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Product removed'


@pytest.mark.django_db
def test_clear_cart(api_client, products_data):
    products = products_data
    product_id = {
        'product': products[0].id,
    }
    api_client.post(reverse('cart:cart-add'), product_id)
    api_client.post(reverse('cart:cart-add'), product_id)
    response = api_client.post(reverse('cart:cart-clear'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Cart cleared'


@pytest.mark.django_db
def test_apply_discount(api_client, discount_factory, products_data):
    products = products_data
    product_id = {
        'product': products[0].id,
    }
    api_client.post(reverse('cart:cart-add'), product_id)
    discount_data = {
        'code': discount_factory.code
    }
    response = api_client.post(reverse('cart:cart-apply-discount'), discount_data)
    assert response.status_code == status.HTTP_200_OK
    assert 'message' in response.data
    assert response.data['message'] == 'discount code Successfully applied'


