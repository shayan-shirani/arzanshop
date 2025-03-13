import pytest
from .factories import *
from django.db import IntegrityError, DataError
from django.core.exceptions import ValidationError
# ---Category Test---
@pytest.mark.django_db()
def test_create_category():
    root_category = ParentCategoryFactory()
    category = CategoryFactory(parent=root_category)
    assert category.parent == root_category
    assert root_category.children.count() == 1
    assert root_category.name == 'Root Category'
    assert category.name == 'Child Category'

# ---Product Test---
@pytest.mark.django_db
def test_create_product():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    product = ProductFactory(category=category, vendor=vendor)
    assert product.category == category
    assert product.vendor == vendor

@pytest.mark.django_db
def test_create_product_without_vendor_or_category():
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(vendor=None, category=None)
    assert 'violates not-null constraint' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_create_product_with_invalid_price():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(price=-1, category=category, vendor=vendor)
    assert 'shop_product_price_check' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_create_product_with_invalid_stock():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(stock=-1, category=category, vendor=vendor)
    assert 'shop_product_stock_check' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_create_product_with_invalid_weight():
    category = CategoryFactory()
    vendor = VendorProfileFactory()
    with pytest.raises(IntegrityError) as excinfo:
        ProductFactory(weight=-1, category=category, vendor=vendor)
    assert 'shop_product_weight_check' in str(excinfo.value).lower()

# ---ShopUser Test---
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
def test_create_shop_user_with_invalid_phone():
    with pytest.raises(DataError) as excinfo:
        ShopUserFactory(phone='0913225489789726')
    assert "value too long for type character varying(11)" in str(excinfo.value).lower()

# --- Addresses Test ---
@pytest.mark.django_db
def test_create_multiple_addresses():
    address1 = AddressFactory()
    address2 = AddressFactory()
    assert address1.street
    assert address1.city
    assert address1.state
    assert address1.country
    assert address1.zip_code
    assert address1.is_default
    assert address2.street
    assert address2.city

# --- VendorProfile Test ---
@pytest.mark.django_db
def test_create_vendor_profile():
    user = ShopUserFactory(role=ShopUser.Roles.VENDOR)
    vendor = VendorProfileFactory(user=user)
    assert vendor.user == user
    assert vendor.store_name
    assert vendor.status == VendorProfile.Status.PENDING
    assert not vendor.is_active
    assert vendor.user.role == ShopUser.Roles.VENDOR

@pytest.mark.django_db
def test_create_vendor_profile_without_user():
    with pytest.raises(IntegrityError) as excinfo:
        VendorProfileFactory(user=None)
    assert 'violates not-null constraint' in str(excinfo.value).lower()

@pytest.mark.django_db
def test_approve_vendor_profile():
    user = ShopUserFactory()
    vendor = VendorProfileFactory(user=user, status=VendorProfile.Status.PENDING)
    vendor.approve()
    assert vendor.status == VendorProfile.Status.APPROVED

@pytest.mark.django_db
def test_approve_vendor_profile():
    user = ShopUserFactory()
    vendor = VendorProfileFactory(user=user, status=VendorProfile.Status.PENDING)
    vendor.reject()
    assert vendor.status == VendorProfile.Status.REJECTED