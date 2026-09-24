import pytest
from django.urls import reverse
from django.utils import timezone

from apps.leads.models import Lead, LeadKind, LeadStatus
from apps.leads.services.intake import LeadInput, submit_lead
from apps.properties.models import PublicationStatus

pytestmark = pytest.mark.django_db


def test_a_general_lead_needs_no_subject():
    lead = submit_lead(
        LeadInput(full_name="Ana Pop", phone_number="0721234567", message="Looking for a flat.")
    )
    assert lead.status == LeadStatus.NEW
    assert lead.subject is None
    assert lead.phone_number == "+40721234567"


def test_a_property_enquiry_is_auto_assigned_to_the_listing_agent(make_property, agent):
    prop = make_property()
    lead = submit_lead(
        LeadInput(
            full_name="Ana Pop",
            phone_number="0721234567",
            kind=LeadKind.PROPERTY,
            property_id=prop.pk,
        )
    )
    assert lead.assigned_to_id == agent.pk
    assert lead.assigned_at is not None
    assert lead.notes.filter(is_system=True).exists()


def test_the_request_id_is_captured_for_correlation():
    lead = submit_lead(LeadInput(full_name="Ana", phone_number="0721234567", message="Hello"))
    assert isinstance(lead.request_id, str)


def test_public_endpoint_rejects_the_honeypot(client, make_property):
    prop = make_property()
    prop.publication_status = PublicationStatus.PUBLISHED
    prop.published_at = timezone.now()
    prop.save(update_fields=["publication_status", "published_at"])

    response = client.post(
        reverse("v1:public:lead-create"),
        {
            "full_name": "Bot",
            "phone_number": "0721234567",
            "property_slug": prop.slug,
            "website": "http://spam.example",
        },
        content_type="application/json",
    )
    assert response.status_code == 400
    assert Lead.objects.count() == 0


def test_public_endpoint_returns_only_a_receipt(client):
    response = client.post(
        reverse("v1:public:lead-create"),
        {"full_name": "Ana Pop", "phone_number": "0721234567", "message": "Interested."},
        content_type="application/json",
    )
    assert response.status_code == 201
    assert set(response.json()["data"]) == {"id", "status", "created_at"}
