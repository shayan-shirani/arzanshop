from django.db import IntegrityError

import pytest

from apps.accounts.tests.factories import VendorProfileFactory

from apps.accounts.models import VendorProfile, ShopUser

@pytest.mark.django_db
def test_create_vendor_profile():
    vendor = VendorProfileFactory()
    assert vendor.user
    assert vendor.store_name
    assert vendor.status == VendorProfile.Status.PENDING
    assert not vendor.is_active
    assert vendor.user.role == ShopUser.Roles.Customer

@pytest.mark.django_db
def test_create_vendor_profile_without_user():
    with pytest.raises(IntegrityError) as excinfo:
        VendorProfileFactory(user=None)
    assert 'violates not-null constraint' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_approve_vendor_profile():
    vendor = VendorProfileFactory()
    vendor.approve()
    assert vendor.status == VendorProfile.Status.APPROVED

@pytest.mark.django_db
def test_approve_vendor_profile():
    vendor = VendorProfileFactory()
    vendor.reject()
    assert vendor.status == VendorProfile.Status.REJECTED
