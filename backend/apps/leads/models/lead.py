"""Contact requests and their handling.

One Lead table covers general contact, property enquiries and development
enquiries. They differ only in what they point at, and splitting them would
force the dashboard to merge three inboxes for no gain. The `kind` field plus
two nullable relations express the difference.

A lead may reference a property, a development, or neither.

Note what a lead is not: it is not a user. Most enquiries come from people
without an account, so contact details are stored on the row. When the sender
happens to be signed in, `user` is filled in as well.
"""

from __future__ import annotations

import builtins

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class LeadStatus(models.TextChoices):
    NEW = "new", _("New")
    CONTACTED = "contacted", _("Contacted")
    QUALIFIED = "qualified", _("Qualified")
    CLOSED = "closed", _("Closed")
    SPAM = "spam", _("Spam")


class LeadKind(models.TextChoices):
    GENERAL = "general", _("General contact")
    PROPERTY = "property", _("Property enquiry")
    DEVELOPMENT = "development", _("Development enquiry")
    VIEWING = "viewing", _("Viewing request")
    VALUATION = "valuation", _("Valuation request")


class ContactPreference(models.TextChoices):
    PHONE = "phone", _("Phone call")
    SMS = "sms", _("Text message")
    EMAIL = "email", _("Email")
    ANY = "any", _("Any")


class LeadQuerySet(models.QuerySet):
    def open(self) -> "LeadQuerySet":
        return self.filter(status__in=[LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.QUALIFIED])

    def unassigned(self) -> "LeadQuerySet":
        return self.filter(assigned_to__isnull=True).exclude(status=LeadStatus.SPAM)


class Lead(BaseModel):
    kind = models.CharField(
        max_length=20, choices=LeadKind.choices, default=LeadKind.GENERAL, db_index=True
    )
    status = models.CharField(
        max_length=16, choices=LeadStatus.choices, default=LeadStatus.NEW, db_index=True
    )

    full_name = models.CharField(max_length=160)
    phone_number = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    contact_preference = models.CharField(
        max_length=10, choices=ContactPreference.choices, default=ContactPreference.ANY
    )
    preferred_time = models.CharField(
        max_length=120, blank=True, help_text=_("Free text, e.g. weekday mornings.")
    )

    property = models.ForeignKey(
        "properties.Property", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="leads",
    )
    development = models.ForeignKey(
        "developments.Development", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="leads",
    )
    unit = models.ForeignKey(
        "developments.Unit", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="leads",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="submitted_leads",
        help_text=_("Set when the sender was signed in."),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_leads",
    )
    assigned_at = models.DateTimeField(null=True, blank=True)

    source_path = models.CharField(
        max_length=255, blank=True, help_text=_("Page the form was submitted from.")
    )
    request_id = models.CharField(
        max_length=64, blank=True, help_text=_("Correlates with the server log for this request.")
    )

    first_response_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    objects = LeadQuerySet.as_manager()

    class Meta:
        verbose_name = _("lead")
        verbose_name_plural = _("leads")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"], name="lead_status_recent_idx"),
            models.Index(fields=["assigned_to", "status"], name="lead_assignee_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_kind_display()})"

    # The `property` field above shadows the builtin inside this class body.
    @builtins.property
    def subject(self):
        """Whatever this lead is about, if anything."""
        return self.property or self.development or self.unit


class LeadNote(BaseModel):
    """The handling history: notes, status changes, assignments.

    Append-only in practice. It is separate from apps.audit because these
    entries are part of the conversation staff have about a lead, shown in the
    dashboard; audit events are a compliance record nobody reads day to day.
    """

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="lead_notes"
    )
    body = models.TextField()
    is_system = models.BooleanField(
        default=False, help_text=_("Generated by a workflow rather than typed by a person.")
    )

    class Meta:
        verbose_name = _("lead note")
        verbose_name_plural = _("lead notes")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Note on {self.lead_id}"
