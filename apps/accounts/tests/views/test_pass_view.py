from django.utils.http import urlsafe_base64_encode
from django.core.cache import cache
from  django.urls import reverse

from rest_framework import status

import pytest

from apps.accounts.services.password_reset_services import PasswordResetService

from apps.accounts.tests.conftest import (
    api_client,
    user_factory,
)

@pytest.mark.django_db
def test_change_password_view(api_client, user_factory, validate_user):
    user = user_factory
    user.set_password('old_strong_password123')
    user.save()
    updated_password = validate_user['password']
    data = {
        'old_password': 'old_strong_password123',
        'new_password': updated_password,
        'confirm_password': updated_password,
    }
    api_client.force_authenticate(user=user)
    response = api_client.put(reverse('accounts:change-password'), data=data)
    assert response.status_code == status.HTTP_200_OK
    assert user.check_password(updated_password)

@pytest.mark.django_db
def test_password_reset_request_view(api_client, user_factory):
    user = user_factory
    data = {
        'email': user.email,
    }
    response = api_client.post(reverse('accounts:password-reset-request'), data=data)
    assert response.status_code == status.HTTP_200_OK
    assert cache.get(f'reset_password_token:{user.pk}') is not None

@pytest.mark.django_db
def test_password_reset_request_invalid_email(api_client):
    data = {
        'email': 'invalid_email',
    }
    response = api_client.post(reverse('accounts:password-reset-request'), data=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'User not found'


@pytest.mark.django_db
def test_password_reset_request_missing_email(api_client):
    data = {}
    response = api_client.post(reverse('accounts:password-reset-request'), data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == 'Email is required'

@pytest.mark.django_db
def test_password_reset_success(api_client, user_factory, validate_user):
    user = user_factory
    updated_password = validate_user['password']
    token = PasswordResetService.generate_reset_password_token(user)
    cache.set(f'reset_password_token:{user.pk}', token)
    uidb64 = urlsafe_base64_encode(str(user.pk).encode())
    data = {
        'new_password': updated_password,
        'new_password_confirm': updated_password
    }
    response = api_client.put(reverse('accounts:password-reset', args=[uidb64, token]), data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'Password reset successfully.'
    user.refresh_from_db()
    assert user.check_password(updated_password)


@pytest.mark.django_db
def test_password_reset_invalid_token(api_client, user_factory, validate_user):
    user = user_factory
    updated_password = validate_user['password']
    cache.set(f'reset_password_token:{user.pk}', 'correct-token')
    uidb64 = urlsafe_base64_encode(str(user.pk).encode())
    data = {
        'new_password': updated_password,
        'new_password_confirm': updated_password
    }
    response = api_client.put(reverse('accounts:password-reset', args=[uidb64, 'wrong-token']), data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == 'Invalid or expired token.'


@pytest.mark.django_db
def test_password_reset_mismatched_passwords(api_client, user_factory, validate_user):
    user = user_factory
    updated_password = validate_user['password']
    token = PasswordResetService.generate_reset_password_token(user)
    cache.set(f'reset_password_token:{user.pk}', token)
    uidb64 = urlsafe_base64_encode(str(user.pk).encode())
    data = {
        'new_password': updated_password,
        'new_password_confirm': 'wrong-password'
    }
    response = api_client.put(reverse('accounts:password-reset', args=[uidb64, token]), data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data
