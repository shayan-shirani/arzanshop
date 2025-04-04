import pytest

from apps.accounts.serializers import AddressSerializer

from apps.accounts.models import Addresses

from .conftest import (
    api_factory,
    validate_user,
    validate_address,
    user_factory,
    address_factory
)

@pytest.mark.django_db
def test_address_serializer(address_factory):
    address = address_factory
    serializer = AddressSerializer(address)

    expected_data = {
        'street': address.street,
        'city': address.city,
        'state': address.state,
        'country': address.country,
        'zip_code': address.zip_code,
        'is_default': address.is_default,
    }

    assert serializer.data == expected_data

@pytest.mark.django_db
def test_address_serializer_create(api_factory, validate_user, validate_address, user_factory):
    data = validate_address
    request = api_factory.post('/addresses/')
    request.user = user_factory
    serializer = AddressSerializer(data=data, context={'request': request})
    assert serializer.is_valid()
    address = serializer.save()
    assert address.user
    assert Addresses.objects.count() == 1

@pytest.mark.django_db
def test_address_serializer_update(api_factory,address_factory):
    request = api_factory.put('/addresses/')
    address = address_factory
    request.user = address.user

    updated_data = {
        'street': '456 Updated St',
        'city': 'UpdatedCity',
        'state': 'UpdatedState',
        'country': 'UpdatedCountry',
        'zip_code': 67890,
        'is_default': False,
    }

    serializer = AddressSerializer(address, data=updated_data, partial=True)
    assert serializer.is_valid()
    updated_address = serializer.save()
    assert updated_address.user == address.user
    assert updated_address.street == updated_data['street']
    assert updated_address.city == updated_data['city']
    assert updated_address.state == updated_data['state']
    assert updated_address.country == updated_data['country']
    assert updated_address.zip_code == updated_data['zip_code']
    assert updated_address.is_default == updated_data['is_default']