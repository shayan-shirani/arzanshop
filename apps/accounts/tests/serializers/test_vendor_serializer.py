import pytest

from apps.accounts.serializers import VendorProfileSerializer

from apps.accounts.models import VendorProfile

from .conftest import (
    api_factory,
    user_factory,
    vendor_factory,
    validate_vendor
)

@pytest.mark.django_db
def test_vendor_serializer(api_factory, vendor_factory):
    vendor = vendor_factory
    serializer = VendorProfileSerializer(vendor)

    expected_data = {
        'user': vendor.user.id,
        'id': vendor.id,
        'status': vendor.status,
        'store_name': vendor.store_name,
        'description': vendor.description,
        'is_active': False
    }

    assert serializer.data == expected_data

@pytest.mark.django_db
def test_vendor_serializer_create(api_factory, validate_vendor, user_factory):
    vendor = validate_vendor
    request = api_factory.post('/vendors/')
    request.user = user_factory
    serializer = VendorProfileSerializer(data=vendor, context={'request': request})
    assert serializer.is_valid()
    vendor = serializer.save()
    assert vendor.user
    assert VendorProfile.objects.count() == 1

@pytest.mark.django_db
def test_vendor_serializer_update(api_factory, vendor_factory, user_factory):
    request = api_factory.put('/vendors/')
    vendor = vendor_factory
    request.user = user_factory
    updated_data = {
        'store_name': 'Updated Store Name',
        'description': 'Updated Description',
        'is_active': True,
    }
    serializer = VendorProfileSerializer(vendor, data=updated_data, partial=True, context={'request': request})
    assert serializer.is_valid()
    updated_vendor = serializer.save()
    assert updated_vendor.store_name == updated_data['store_name']