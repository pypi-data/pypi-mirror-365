import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def create_user():
    email = "testuser@test.com"
    password = "somepassword123"
    user = User.objects.create_user(email=email)
    user.USERNAME_FIELD = "email"
    user.set_password(password)
    user.save()
    user.secret = "somesecret"
    return email, password, user


GET_TOKEN_URL = reverse("get_token")


@pytest.mark.parametrize(
    ["request_data", "expected_errors"],
    [
        ({"email": "<EMAIL>"}, {"password": ["This field is required."]}),
        ({}, {"email": ["This field is required."], "password": ["This field is required."]}),
        (
            {"email": "<EMAIL>", "password": "pass"},
            {"non_field_errors": ["Unable to authenticate with provided credentials"]},
        ),
    ],
)
@pytest.mark.django_db
def test_get_token_bad_credentials(request_data, expected_errors):
    client = APIClient()
    response = client.post(GET_TOKEN_URL, request_data)
    assert response.status_code == 400
    assert response.json() == expected_errors


@pytest.mark.django_db
def test_get_token(create_user):
    email, password, *_ = create_user
    client = APIClient()
    response = client.post(GET_TOKEN_URL, {"email": email, "password": password})
    assert response.status_code == 201
    assert response.json().get("token") is not None, "Expect token in response"
    assert response.json().get("created") is not None, "Expect token in response"


@pytest.mark.django_db
def test_revoke_token(create_user):
    email, password, user = create_user
    old_secret = user.secret
    client = APIClient()
    response = client.post(GET_TOKEN_URL, {"email": email, "password": password})
    token = response.json().get("token")
    client.credentials(HTTP_AUTHORIZATION="JWT " + token)
    response = client.post(reverse("revoke_token"), {})
    assert response.status_code == 201
    user = User.objects.get(email=email)
    assert user.secret != old_secret, "Expect secret to be changed after revoking token"
