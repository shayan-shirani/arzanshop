from rest_framework.exceptions import ValidationError
from uuid import UUID

import pytest

from apps.accounts.serializers import (
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer,
    LoginSerializer,
    LoginVerifySerializer
)

from apps.accounts.tests.factories import ShopUserFactory
from apps.accounts.tests.conftest import api_factory


@pytest.mark.parametrize(
    'email, expected_valid', [
        ('test@example.com', True),
        ('invalid-email', False),
        ('', False),
        (None, False)
    ]
)
def test_pass_reset_request_serializer(email, expected_valid):
    data = {
        'email': email
    }
    serializer = PasswordResetRequestSerializer(data=data)
    assert serializer.is_valid() == expected_valid

    if not expected_valid:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
    else:
        assert serializer.validated_data['email'] == email

@pytest.mark.parametrize(
    'new_password, new_password_confirm, expected_valid', [
        ('new_test_password', 'new_test_password', True),
        ('new_test_password', 'invalid_password', False),
        ('', '', False),
        (None, None, False)
    ]
)
def test_pass_reset_serializer(new_password, new_password_confirm, expected_valid):
    data = {
        'new_password': new_password,
        'new_password_confirm': new_password_confirm
    }
    serializer = PasswordResetSerializer(data=data)
    assert serializer.is_valid() == expected_valid

    if not expected_valid:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
    else:
        assert serializer.validated_data['new_password'] == new_password
        assert serializer.validated_data['new_password_confirm'] == new_password_confirm

@pytest.mark.parametrize(
    'old_password, new_password, confirm_password, expected_valid', [
        ('test_password', 'new_test_password', 'new_test_password', True),
        ('test_password', 'new_test_password', 'invalid_password', False),
        ('', '', '', False),
        (None, None, None, False)
    ]
)
@pytest.mark.django_db
def test_pass_change_serializer(
        api_factory, old_password, new_password, confirm_password, expected_valid
):
    fake_user = ShopUserFactory()
    fake_user.set_password('test_password')
    fake_user.save()

    request = api_factory.put('/change-password/')
    request.user = fake_user
    data = {
        'old_password': old_password,
        'new_password': new_password,
        'confirm_password': confirm_password
    }
    serializer = PasswordChangeSerializer(fake_user, data=data, context={'request': request})
    assert serializer.is_valid() == expected_valid

    if not expected_valid:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
    else:
        serializer.save()
        assert fake_user.check_password(new_password)
