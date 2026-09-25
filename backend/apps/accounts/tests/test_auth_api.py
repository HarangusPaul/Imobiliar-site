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


def test_session_returns_the_signed_in_account(client):
    client.post(
        reverse("v1:client:register"),
        {"phone_number": "0721234567", "password": "correct-horse-battery"},
        content_type="application/json",
    )
    assert client.get(reverse("v1:client:session")).status_code in (401, 403)

    client.post(
        reverse("v1:client:login"),
        {"phone_number": "0721234567", "password": "correct-horse-battery"},
        content_type="application/json",
    )
    session = client.get(reverse("v1:client:session"))
    assert session.status_code == 200
    assert session.json()["data"]["phone_number"] == "+40721234567"


def test_login_without_remember_expires_with_the_browser(client):
    client.post(
        reverse("v1:client:register"),
        {"phone_number": "0721234567", "password": "correct-horse-battery"},
        content_type="application/json",
    )
    client.post(
        reverse("v1:client:login"),
        {"phone_number": "0721234567", "password": "correct-horse-battery", "remember": False},
        content_type="application/json",
    )
    assert client.session.get_expire_at_browser_close()
