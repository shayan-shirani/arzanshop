from  django.urls import reverse

from rest_framework import status

from apps.accounts.models import ShopUser

import pytest

from apps.accounts.tests.conftest import api_client, user_factory, validate_user
from apps.accounts.tests.factories import ShopUserFactory


@pytest.mark.django_db
def test_list_user_when_admin(api_client):
    user = ShopUserFactory(is_superuser=True, is_staff=True)
    api_client.force_authenticate(user=user)
    ShopUserFactory.create_batch(5)
    response = api_client.get(reverse('accounts:users-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 6

@pytest.mark.django_db
def test_list_user_unauthenticated(api_client):
    ShopUserFactory.create_batch(5)
    response = api_client.get(reverse('accounts:users-list'))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_list_user_when_customer(api_client):
    user = ShopUserFactory(is_superuser=False, is_staff=False)
    api_client.force_authenticate(user=user)
    ShopUserFactory.create_batch(5)
    response = api_client.get(reverse('accounts:users-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_retrieve_user(api_client, user_factory):
    user = user_factory
    api_client.force_authenticate(user=user)
    ShopUserFactory.create()
    response = api_client.get(reverse('accounts:users-detail', args=[user.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == user.username

@pytest.mark.django_db
def test_retrieve_user_unauthenticated(api_client, user_factory):
    user = user_factory
    response = api_client.get(reverse('accounts:users-detail', args=[user.id]))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_retrieve_user_when_not_found(api_client, user_factory):
    user = user_factory
    api_client.force_authenticate(user=user)
    response = api_client.get(reverse('accounts:users-detail', args=[999]))
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_create_user(api_client, validate_user):
    data = validate_user
    response = api_client.post(reverse('accounts:users-list'), data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['username'] == data['username']

@pytest.mark.parametrize(
    'phone, email', [
        (12345, 'invalid-email'),
        ('', 'invalid-email'),
        ('', ''),
        (12345, ''),
    ]
)
@pytest.mark.django_db
def test_create_user_invalid_data(api_client, validate_user, phone, email):
    data = validate_user
    data['phone'] = phone
    data['email'] = email
    response = api_client.post(reverse('accounts:users-list'), data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_update_user(api_client, user_factory, validate_user):
    user = user_factory
    data = validate_user
    api_client.force_authenticate(user=user)
    response = api_client.put(reverse('accounts:users-detail', args=[user.id]), data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == data['username']

@pytest.mark.django_db
def test_update_user_unauthenticated(api_client, user_factory, validate_user):
    user = user_factory
    data = validate_user
    response = api_client.put(reverse('accounts:users-detail', args=[user.id]), data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize(
    'phone, email', [
        (12345, 'invalid-email'),
        ('', 'invalid-email'),
        ('', ''),
        (12345, ''),
    ]
)
@pytest.mark.django_db
def test_update_user_invalid_data(api_client, user_factory, validate_user, phone, email):
    user = user_factory
    data = validate_user
    data['phone'] = phone
    data['email'] = email
    api_client.force_authenticate(user=user)
    response = api_client.put(reverse('accounts:users-detail', args=[user.id]), data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_delete_user(api_client, user_factory):
    user = user_factory
    api_client.force_authenticate(user=user)
    response = api_client.delete(reverse('accounts:users-detail', args=[user.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ShopUser.objects.filter(id=user.id).exists()

@pytest.mark.django_db
def test_delete_user_unauthenticated(api_client, user_factory):
    user = user_factory
    response = api_client.delete(reverse('accounts:users-detail', args=[user.id]))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED