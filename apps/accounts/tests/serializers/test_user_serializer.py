import pytest

from apps.accounts.serializers import UserRegistrationSerializer

from .conftest import api_factory, validate_user


@pytest.mark.django_db
def test_user_registration_serializer(api_factory, validate_user):
    data = validate_user
    request = api_factory.post('/users/', data)
    serializer = UserRegistrationSerializer(data=data, context={'request': request})
    assert serializer.is_valid(), serializer.errors
    shop_user = serializer.save()
    assert shop_user.username == data['username']
    assert shop_user.email == data['email']
    assert shop_user.first_name == data['first_name']
    assert shop_user.check_password(data['password'])

@pytest.mark.django_db
def test_user_registration_serializer_invalid_phone(api_factory, validate_user):
    data = validate_user
    data['phone'] = '12345'
    request = api_factory.post('/users/', data)
    serializer = UserRegistrationSerializer(data=data, context={'request': request})
    assert not serializer.is_valid()
    assert 'phone' in serializer.errors
    assert serializer.errors['phone']['error'] == 'Phone number must be 11 digits'
