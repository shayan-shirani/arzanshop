from django.urls import reverse
from rest_framework import status

import pytest

from apps.accounts.services.jwt import JwtService


@pytest.mark.django_db
def test_logout_with_valid_token(api_client, user_factory):
    user = user_factory
    tokens = JwtService.generate_token(user)
    refresh_token = tokens['refresh']
    data = {
        'refresh': refresh_token
    }
    api_client.force_authenticate(user=user)
    response = api_client.post(reverse('accounts:logout'), data=data, format='json')
    assert response.status_code == status.HTTP_205_RESET_CONTENT
    assert response.data['message'] == 'Logout successful!'

@pytest.mark.django_db
def test_logout_missing_token(api_client, user_factory):
    user = user_factory
    data = {}
    api_client.force_authenticate(user=user)
    response = api_client.post(reverse('accounts:logout'), data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == 'Refresh token is required'

@pytest.mark.django_db
def test_logout_with_invalid_token(api_client, user_factory):
    user = user_factory
    tokens = JwtService.generate_token(user)
    refresh_token = tokens['refresh']
    invalid_token = refresh_token + 'invalid'
    data = {'refresh': invalid_token}
    api_client.force_authenticate(user=user)
    response = api_client.post(reverse('accounts:logout'), data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == 'Invalid refresh token'
