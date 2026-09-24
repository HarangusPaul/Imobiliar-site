import pytest

from apps.content.models import PresentationPage

pytestmark = pytest.mark.django_db


def test_seo_fields_fall_back_to_the_page_content():
    page = PresentationPage.objects.create(
        slug="about", title="About us", summary="Who we are and what we do."
    )
    assert page.resolved_seo_title(page.title) == "About us"
    assert page.resolved_seo_description(page.summary) == "Who we are and what we do."


def test_explicit_seo_values_win():
    page = PresentationPage.objects.create(
        slug="about",
        title="About us",
        seo_title="About our agency",
        seo_description="Independent agency covering the whole city.",
    )
    assert page.resolved_seo_title(page.title) == "About our agency"
    assert page.resolved_seo_description("ignored").startswith("Independent agency")


def test_a_long_fallback_description_is_truncated():
    page = PresentationPage.objects.create(slug="terms", title="Terms")
    assert len(page.resolved_seo_description("x" * 400)) == 160
