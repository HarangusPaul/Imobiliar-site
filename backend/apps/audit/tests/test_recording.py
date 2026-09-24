import pytest

from apps.audit.models import AuditEvent
from apps.audit.selectors.trail import for_target
from apps.audit.services.recording import record_event

pytestmark = pytest.mark.django_db


def test_an_event_captures_the_actor_and_target(make_property, staff):
    prop = make_property()
    event = record_event(actor=staff, action="property.updated", target=prop,
                         metadata={"changed": ["price"]})

    assert event.target_app == "properties"
    assert event.target_model == "property"
    assert event.target_uuid == prop.uuid
    assert event.actor_label == staff.get_full_name()
    assert event.metadata["changed"] == ["price"]


def test_events_cannot_be_modified(make_property, staff):
    event = record_event(actor=staff, action="property.updated", target=make_property())
    event.action = "property.tampered"
    with pytest.raises(ValueError):
        event.save()


def test_events_cannot_be_deleted(make_property, staff):
    event = record_event(actor=staff, action="property.updated", target=make_property())
    with pytest.raises(ValueError):
        event.delete()


def test_the_actor_label_survives_a_deleted_account(make_property, staff):
    prop = make_property()
    record_event(actor=staff, action="property.updated", target=prop)
    label = staff.get_full_name()
    staff.delete()

    event = AuditEvent.objects.get(action="property.updated", target_uuid=prop.uuid)
    assert event.actor is None
    assert event.actor_label == label


def test_recording_never_breaks_the_caller(staff):
    class Broken:
        _meta = None

        def __str__(self):
            raise RuntimeError("boom")

    assert record_event(actor=staff, action="thing.done", target=Broken()) is None


def test_the_trail_for_an_object_is_retrievable(make_property, staff):
    prop = make_property()
    record_event(actor=staff, action="property.updated", target=prop)
    record_event(actor=staff, action="property.published", target=prop)
    assert for_target(prop).count() == 2
