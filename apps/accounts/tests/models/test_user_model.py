from django.db import DataError

import pytest

from apps.accounts.tests.factories import ShopUserFactory

from apps.accounts.models import ShopUser

@pytest.mark.django_db
def test_create_shop_user():
    user = ShopUserFactory()
    assert user.first_name
    assert user.last_name
    assert user.username
    assert user.email
    assert user.phone
    assert user.role == ShopUser.Roles.Customer
    assert user.is_active
    assert user.role in [ShopUser.Roles.ADMIN, ShopUser.Roles.VENDOR, ShopUser.Roles.Customer]
    assert str(user) == user.username

@pytest.mark.django_db
def test_create_shop_user_with_invalid_phone_length():
    with pytest.raises(DataError) as excinfo:
        ShopUserFactory(phone='0913225489789726')
    assert 'value too long for type character varying(11)' in str(excinfo.value).lower()