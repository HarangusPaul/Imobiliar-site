import pytest

from core.api.exceptions import NotAllowedError

from apps.leads.models import LeadStatus
from apps.leads.services.intake import LeadInput, submit_lead
from apps.leads.services.workflow import (
    InvalidLeadTransitionError,
    assign_lead,
    change_status,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def lead(db):
    return submit_lead(LeadInput(full_name="Ana Pop", phone_number="0721234567", message="Hi"))


def test_first_contact_stamps_the_response_time(lead, staff):
    change_status(lead, target=LeadStatus.CONTACTED, actor=staff)
    lead.refresh_from_db()
    assert lead.first_response_at is not None


def test_spam_is_terminal(lead, staff):
    change_status(lead, target=LeadStatus.SPAM, actor=staff)
    with pytest.raises(InvalidLeadTransitionError):
        change_status(lead, target=LeadStatus.CONTACTED, actor=staff)


def test_a_closed_lead_can_only_be_reopened_as_qualified(lead, staff):
    change_status(lead, target=LeadStatus.CLOSED, actor=staff)
    with pytest.raises(InvalidLeadTransitionError):
        change_status(lead, target=LeadStatus.CONTACTED, actor=staff)
    change_status(lead, target=LeadStatus.QUALIFIED, actor=staff)


def test_every_transition_leaves_a_note(lead, staff):
    change_status(lead, target=LeadStatus.CONTACTED, actor=staff)
    change_status(lead, target=LeadStatus.QUALIFIED, actor=staff)
    assert lead.notes.count() == 2


def test_an_agent_cannot_assign_leads(lead, agent):
    with pytest.raises(NotAllowedError):
        assign_lead(lead, assignee=agent, actor=agent)


def test_staff_can_assign(lead, staff, agent):
    assign_lead(lead, assignee=agent, actor=staff)
    lead.refresh_from_db()
    assert lead.assigned_to_id == agent.pk
