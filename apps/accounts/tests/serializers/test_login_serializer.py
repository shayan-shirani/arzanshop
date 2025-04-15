from rest_framework.exceptions import ValidationError

from uuid import UUID
import pytest

from apps.accounts.serializers import LoginSerializer, LoginVerifySerializer

@pytest.mark.parametrize(
    'username, expected_valid', [
        ('test12Z', True),
        ('', False),
        (None, False),
    ]
)
def test_login_serializer(username, expected_valid):
    data = {
        'username': username
    }
    serializer = LoginSerializer(data=data)
    assert serializer.is_valid() == expected_valid

    if not expected_valid:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
    else:
        assert serializer.validated_data['username'] == username

@pytest.mark.parametrize(
    'request_id, password, expected_valid', [
        ('3b21fd4c-ccc8-406d-81b0-cb4530e81884', 'test_password', True),
        ('', '', False),
        (None, None, False),
    ]
)
def test_login_verify_serializer(request_id, password, expected_valid):
    data = {
        'request_id': request_id,
        'password': password
    }
    serializer = LoginVerifySerializer(data=data)
    assert serializer.is_valid() == expected_valid

    if not expected_valid:
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
    else:
        assert serializer.validated_data['request_id'] ==  UUID(request_id)
        assert serializer.validated_data['password'] == password