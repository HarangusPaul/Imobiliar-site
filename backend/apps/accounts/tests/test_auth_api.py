import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_register_login_logout_round_trip(client):
    register = client.post(
        reverse("v1:client:register"),
        {"phone_number": "0721234567", "password": "correct-horse-battery"},
        content_type="application/json",
    )
    assert register.status_code == 201
    assert register.json()["data"]["phone_number"] == "+40721234567"
    assert "password" not in register.json()["data"]

    login = client.post(
        reverse("v1:client:login"),
        {"phone_number": "+40721234567", "password": "correct-horse-battery"},
        content_type="application/json",
    )
    assert login.status_code == 200
    assert login.json()["data"]["roles"] == ["client"]

    assert client.post(reverse("v1:client:logout")).status_code == 204


def test_bad_credentials_use_the_standard_error_envelope(client):
    response = client.post(
        reverse("v1:client:login"),
        {"phone_number": "+40721234567", "password": "nope"},
        content_type="application/json",
    )
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "invalid_credentials"
    assert error["request_id"]
