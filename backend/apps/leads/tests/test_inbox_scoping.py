import pytest

from apps.leads.selectors.inbox import dashboard_inbox
from apps.leads.services.intake import LeadInput, submit_lead

pytestmark = pytest.mark.django_db


def test_an_agent_sees_only_their_own_pipeline(make_property, agent, staff):
    own = submit_lead(
        LeadInput(full_name="Mine", phone_number="0721000010", property_id=make_property().pk)
    )
    submit_lead(LeadInput(full_name="Someone else", phone_number="0721000011", message="Hi"))

    visible = dashboard_inbox(agent)
    assert [lead.pk for lead in visible] == [own.pk]


def test_staff_see_everything(make_property, agent, staff):
    submit_lead(LeadInput(full_name="A", phone_number="0721000010", property_id=make_property().pk))
    submit_lead(LeadInput(full_name="B", phone_number="0721000011", message="Hi"))

    assert dashboard_inbox(staff).count() == 2
