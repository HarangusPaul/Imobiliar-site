"""The endpoint scaffold exists and is wired into the right zone."""

from __future__ import annotations

import pytest
from django.urls import resolve, reverse

EXPECTED = [
    ("v1:client:register", "/api/v1/client/auth/register/"),
    ("v1:client:login", "/api/v1/client/auth/login/"),
    ("v1:client:logout", "/api/v1/client/auth/logout/"),
    ("v1:public:property-list", "/api/v1/public/properties/"),
    ("v1:public:development-list", "/api/v1/public/developments/"),
    ("v1:public:lead-create", "/api/v1/public/leads/"),
    ("v1:dashboard:property-list", "/api/v1/dashboard/properties/"),
    ("v1:dashboard:property-create", "/api/v1/dashboard/properties/create/"),
    ("v1:dashboard:lead-list", "/api/v1/dashboard/leads/"),
]


@pytest.mark.parametrize(("name", "path"), EXPECTED)
def test_endpoint_is_registered_at_the_expected_path(name, path):
    assert reverse(name) == path


@pytest.mark.parametrize(
    ("slug_name", "path"),
    [
        ("v1:public:property-detail", "/api/v1/public/properties/some-listing/"),
        ("v1:public:development-detail", "/api/v1/public/developments/green-park/"),
    ],
)
def test_detail_endpoints_resolve_by_slug(slug_name, path):
    assert resolve(path).view_name == slug_name


@pytest.mark.django_db
def test_dashboard_endpoints_reject_anonymous_callers(client):
    for path in ("/api/v1/dashboard/properties/", "/api/v1/dashboard/leads/"):
        assert client.get(path).status_code in (401, 403)


@pytest.mark.django_db
def test_public_endpoints_are_open(client):
    assert client.get("/api/v1/public/properties/").status_code == 200
