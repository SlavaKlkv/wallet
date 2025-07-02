import pytest
from rest_framework.test import APIClient

from core.constants import USER_LOGIN_URL


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(
        username="testuser", email="testuser@email.com", password="1234567"
    )
    user.plaintext_password = "1234567"
    return user


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(
        username="testuser2", email="testuser2@email.com", password="1234567"
    )


@pytest.fixture
def token_user(user, client):
    response = client.post(
        USER_LOGIN_URL, {"email": "testuser@email.com", "password": "1234567"}
    )
    token = response.data.get("auth_token")
    return token


@pytest.fixture
def token_user_2(user_2, client):
    response = client.post(
        USER_LOGIN_URL, {"email": "testuser2@email.com", "password": "1234567"}
    )
    token = response.data.get("auth_token")
    return token


@pytest.fixture
def auth_client(token_user, client):
    client.credentials(HTTP_AUTHORIZATION=f"Token {token_user}")
    return client


@pytest.fixture
def auth_client_2(token_user_2, client):
    client.credentials(HTTP_AUTHORIZATION=f"Token {token_user_2}")
    return client
