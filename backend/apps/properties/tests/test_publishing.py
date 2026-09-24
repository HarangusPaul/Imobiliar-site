import pytest

from core.api.exceptions import NotAllowedError

from apps.properties.models import PublicationStatus
from apps.properties.services.publishing import (
    InvalidTransitionError,
    NotReadyToPublishError,
    transition_publication,
)

pytestmark = pytest.mark.django_db


def test_a_new_listing_starts_as_a_draft(make_property):
    assert make_property().publication_status == PublicationStatus.DRAFT


def test_an_agent_cannot_publish(make_property, agent):
    prop = make_property()
    with pytest.raises(NotAllowedError):
        transition_publication(prop, target=PublicationStatus.PUBLISHED, actor=agent)


def test_publishing_requires_a_cover_image(make_property, staff):
    prop = make_property()
    with pytest.raises(NotReadyToPublishError) as exc:
        transition_publication(prop, target=PublicationStatus.PUBLISHED, actor=staff)
    assert "cover_image" in exc.value.details["missing"]


def test_archived_cannot_jump_straight_back_to_published(make_property, staff):
    prop = make_property()
    transition_publication(prop, target=PublicationStatus.ARCHIVED, actor=staff)
    with pytest.raises(InvalidTransitionError):
        transition_publication(prop, target=PublicationStatus.PUBLISHED, actor=staff)


def test_every_transition_is_recorded_in_the_audit_log(make_property, staff):
    from apps.audit.models import AuditEvent

    prop = make_property()
    transition_publication(prop, target=PublicationStatus.ARCHIVED, actor=staff)
    assert AuditEvent.objects.filter(action="property.archived", target_uuid=prop.uuid).exists()
