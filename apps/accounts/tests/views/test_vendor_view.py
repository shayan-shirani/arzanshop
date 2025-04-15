from  django.urls import reverse

from rest_framework import status

from apps.accounts.models import VendorProfile

import pytest

from apps.accounts.tests.conftest import (
    api_client,
    user_factory,
    validate_vendor
)
from apps.accounts.tests.factories import VendorProfileFactory, ShopUserFactory


@pytest.mark.django_db
def test_list_vendors(api_client, user_factory):
    user = user_factory
    api_client.force_authenticate(user=user)
    VendorProfileFactory.create(user=user)
    response = api_client.get(reverse('accounts:vendor_profile-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_retrieve_vendor(api_client, user_factory):
    user = user_factory
    api_client.force_authenticate(user=user)
    vendor = VendorProfileFactory(user=user)
    response = api_client.get(reverse('accounts:vendor_profile-detail', args=[vendor.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['store_name'] == vendor.store_name

@pytest.mark.django_db
def test_create_vendor(api_client, user_factory, validate_vendor):
    user = user_factory
    api_client.force_authenticate(user=user)
    data = validate_vendor
    response = api_client.post(reverse('accounts:vendor_profile-list'), data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['store_name'] == data['store_name']

@pytest.mark.django_db
def test_create_vendor_unauthenticated(api_client, validate_vendor):
    data = validate_vendor
    response = api_client.post(reverse('accounts:vendor_profile-list'), data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_update_vendor(api_client, user_factory, validate_vendor):
    user = ShopUserFactory()
    api_client.force_authenticate(user=user)
    vendor = VendorProfileFactory(user=user)
    data = validate_vendor
    response = api_client.put(reverse('accounts:vendor_profile-detail', args=[vendor.id]), data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['store_name'] == data['store_name']

@pytest.mark.django_db
def test_update_vendor_unauthenticated(api_client, validate_vendor):
    data = validate_vendor
    vendor = VendorProfileFactory()
    response = api_client.put(reverse('accounts:vendor_profile-detail', args=[vendor.id]), data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_delete_vendor(api_client, user_factory, validate_vendor):
    user = user_factory
    api_client.force_authenticate(user=user)
    vendor = VendorProfileFactory(user=user)
    response = api_client.delete(reverse('accounts:vendor_profile-detail', args=[vendor.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not VendorProfile.objects.filter(id=vendor.id).exists()