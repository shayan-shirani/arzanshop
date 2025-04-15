import pytest
from django.urls import reverse
from rest_framework import status
from django.core.cache import cache
from unittest.mock import patch

@pytest.mark.django_db
def test_login_with_valid_email(api_client, user_factory):
    user = user_factory
    data = {
        'username': user.email
    }
    response = api_client.post(reverse('accounts:login-request'), data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Please enter your password'
    assert 'request_id' in response.data
    cached = cache.get(f"user_email:{response.data['request_id']}")
    assert cached == user.email

@pytest.mark.django_db
def test_login_with_invalid_email(api_client):
    response = api_client.post(reverse('accounts:login-request'),data={'username': 'invalid_email'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == 'Invalid username'

@pytest.mark.django_db
@patch('apps.accounts.views.PasswordResetService.send_otp')
def test_login_with_valid_phone(mock_send_otp, api_client, user_factory):
    user = user_factory
    data = {
        'username': user.phone,
    }
    response = api_client.post(reverse('accounts:login-request'),data=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'OTP has been sent to your email'
    assert 'request_id' in response.data
    mock_send_otp.assert_called_once_with(user.phone, user.email)
    cached = cache.get(f"user_phone:{response.data['request_id']}")
    assert cached == user.phone

@pytest.mark.django_db
def test_login_with_invalid_phone(api_client):
    data = {
        'username': '09999999999',
    }
    response = api_client.post(reverse('accounts:login-request'),data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == 'Invalid phone number'

@pytest.mark.django_db
def test_login_missing_username(api_client):
    response = api_client.post(reverse('accounts:login-request'),data={})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'username' in response.data
