from django.db import IntegrityError

import pytest

from apps.accounts.tests.factories import AddressFactory

@pytest.mark.django_db
def test_create_address():
    address = AddressFactory()
    assert address.user
    assert address.street
    assert address.state
    assert address.city
    assert address.zip_code
    assert address.country

@pytest.mark.django_db
def test_create_address_without_user():
    with pytest.raises(IntegrityError) as excinfo:
        AddressFactory(user=None)
    assert 'violates not-null constraint' in str(excinfo.value).lower()