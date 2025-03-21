from api.serializers import *
import pytest
from .factories import *
from rest_framework.test import APIRequestFactory

@pytest.fixture
def api_factory():
    return APIRequestFactory()


@pytest.fixture
def user_factory():
    return ShopUserFactory()

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
    address_data =[
    {'street': '123 Test St', 'city': 'TestCity', 'state': 'TestState',
     'country': 'TestCountry', 'zip_code': 12345, 'is_default': True},
    {'street': '456 Updated St', 'city': 'UpdatedCity', 'state': 'UpdatedState',
     'country': 'UpdatedCountry', 'zip_code': 67890, 'is_default': False},
    ]
    return address_data

def assert_address(saved_address, data):
    assert saved_address.street == data['street']
    assert saved_address.city == data['city']
    assert saved_address.state == data['state']
    assert saved_address.country == data['country']
    assert saved_address.zip_code == data['zip_code']
    assert saved_address.is_default == data['is_default']

@pytest.mark.django_db
def test_address_serializer(user_factory):
    address = AddressFactory(user=user_factory)
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
def test_address_serializer_create(api_factory, user_factory):
    request = api_factory.post('/addresses/')
    request.user = user_factory

    data = {
        'street': '123 Test St',
        'city': 'TestCity',
        'state': 'TestState',
        'country': 'TestCountry',
        'zip_code': 12345,
        'is_default': True,
    }

    serializer = AddressSerializer(data=data, context={'request': request})
    assert serializer.is_valid()

    address = serializer.save()
    assert address.user == user_factory
    assert Addresses.objects.count() == 1
    saved_address = Addresses.objects.first()
    assert saved_address.user == user_factory
    assert_address(saved_address, data)

@pytest.mark.django_db
def test_address_serializer_update(user_factory):
    address = AddressFactory(user=user_factory)

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

    assert_address(updated_address, updated_data)

@pytest.mark.django_db
def test_address_serializer_delete(user_factory):
    address = AddressFactory(user=user_factory)
    address_id = address.id

    address.delete()
    assert not Addresses.objects.filter(id=address_id).exists()

@pytest.mark.parametrize('data', [
    {'street': '123 Test St', 'city': 'TestCity', 'state': 'TestState',
     'country': 'TestCountry', 'zip_code': 12345, 'is_default': True},
    {'street': '456 Updated St', 'city': 'UpdatedCity', 'state': 'UpdatedState',
     'country': 'UpdatedCountry', 'zip_code': 67890, 'is_default': False},
])
@pytest.mark.django_db
def test_multiple_address_serializer_create(api_factory, user_factory, data):
    request = api_factory.post('/addresses/')
    request.user = user_factory
    serializer = AddressSerializer(data=data, context={'request': request})
    assert serializer.is_valid()

@pytest.mark.django_db
def test_user_registration_serializer(validate_user, validate_address, api_factory):
    data = validate_user
    request = api_factory.post('/users/', data)
    serializer = UserRegistrationSerializer(data=data, context={'request': request})
    assert serializer.is_valid()
    shop_user = serializer.save()
    assert shop_user.username == data['username']
    assert shop_user.email == data['email']
    assert shop_user.first_name == data['first_name']
    assert shop_user.check_password(data['password'])

@pytest.mark.django_db
def test_user_registration_serializer_invalid_phone(validate_user, validate_address, api_factory):
    data = validate_user
    data['phone'] = '1234567'
    request = api_factory.post('/users/', data)
    serializer = UserRegistrationSerializer(data=data, context={'request': request})
    assert not serializer.is_valid()
    assert 'phone' in serializer.errors
    assert serializer.errors['phone'][0] == 'Phone number must be 11 digits'


@pytest.mark.django_db
def test_vendor_profile_serializer(user_factory, api_factory):
    user_data = user_factory
    vendor_data = {
        'status':VendorProfile.Status.PENDING,
        'store_name':'Test Store',
        'is_active':False,
    }
    request = api_factory.post('/vendor-profiles/', vendor_data)
    request.user = user_data
    serializer = VendorProfileSerializer(data=vendor_data, context={'request': request})
    assert serializer.is_valid()
    vendor = serializer.save()
    assert vendor.user.username == user_data.username
    assert vendor.status == VendorProfile.Status.PENDING
    assert vendor.store_name == vendor_data['store_name']
    assert not vendor.is_active

@pytest.mark.django_db
def test_category_create_serializer():
    root_category = ParentCategoryFactory()
    child_category = CategoryFactory(parent=root_category)
    convert_to_dict = {
        'parent': {
            'name':child_category.parent.name
        },
        'name':child_category.name,
    }
    serializer = CategorySerializer(data=convert_to_dict)
    assert serializer.is_valid()
    category = serializer.save()
    assert child_category.parent.name == convert_to_dict['parent']['name']
    assert category.name == convert_to_dict['name']

@pytest.mark.django_db
def product_serializer_create(api_factory, user_factory):
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
        'category': {child_category.id}
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
