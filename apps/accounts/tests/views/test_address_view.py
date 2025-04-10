from  django.urls import reverse

from rest_framework import status

from apps.accounts.models import Addresses

import pytest

from apps.accounts.tests.conftest import (
    api_client,
    address_factory,
    validate_address,
    user_factory
)
from apps.accounts.tests.factories import AddressFactory

@pytest.mark.django_db
def test_list_addresses(api_client, address_factory, user_factory):
    user = user_factory
    api_client.force_authenticate(user=user)
    AddressFactory.create_batch_with_default(5, user=user)
    response = api_client.get(reverse('accounts:addresses-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5

@pytest.mark.django_db
def test_list_addresses_unauthenticated(api_client, address_factory):
    AddressFactory.create_batch_with_default(5)
    response = api_client.get(reverse('accounts:addresses-list'))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_retrieve_address(api_client, address_factory, user_factory):
    user = user_factory
    api_client.force_authenticate(user=user)
    address = AddressFactory(user=user)
    response = api_client.get(reverse('accounts:addresses-detail', args=[address.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['street'] == address.street

@pytest.mark.django_db
def test_retrieve_address_unauthenticated(api_client, address_factory):
    address = address_factory
    response = api_client.get(reverse('accounts:addresses-detail', args=[address.id]))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_address(api_client, user_factory, validate_address):
    user = user_factory
    api_client.force_authenticate(user=user)
    data = validate_address
    response = api_client.post(reverse('accounts:addresses-list'), data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['street'] == data['street']

@pytest.mark.django_db
def test_create_address_unauthenticated(api_client, validate_address):
    data = validate_address
    response = api_client.post(reverse('accounts:addresses-list'), data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_update_address(api_client, address_factory, user_factory, validate_address):
    user = user_factory
    api_client.force_authenticate(user=user)
    address = AddressFactory(user=user)
    data = validate_address
    response = api_client.put(reverse('accounts:addresses-detail', args=[address.id]), data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['street'] == data['street']

@pytest.mark.django_db
def test_update_address_unauthenticated(api_client, validate_address):
    data = validate_address
    address = AddressFactory()
    response = api_client.put(reverse('accounts:addresses-detail', args=[address.id]), data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_delete_address(api_client, address_factory, user_factory, validate_address):
    user = user_factory
    api_client.force_authenticate(user=user)
    address = AddressFactory(user=user)
    response = api_client.delete(reverse('accounts:addresses-detail', args=[address.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Addresses.objects.filter(id=address.id).exists()