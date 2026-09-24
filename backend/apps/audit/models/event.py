"""Append-only audit events.

Design constraints that follow from "append-only":

* No updated_at, no soft delete, no editable fields. The model inherits the
  UUID base but declares its own created_at, because a row that can be
  modified is not an audit record.
* The target is stored denormalised (label, uuid, app, model) rather than as a
  foreign key. A foreign key would cascade or protect; an audit trail has to
  survive the deletion of the thing it describes, and has to keep reading
  sensibly afterwards.
* The actor is a nullable SET_NULL foreign key, with the actor label copied
  onto the row for the same reason.
* request_id ties an event back to the server log line and to every other
  event from the same request.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UUIDModel


class AuditEvent(UUIDModel):
    action = models.CharField(
        max_length=80,
        db_index=True,
        help_text=_("Dotted action name owned by the emitting app, e.g. property.published."),
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    actor_label = models.CharField(
        max_length=160, blank=True, help_text=_("Who acted, preserved if the account is removed.")
    )

    target_app = models.CharField(max_length=60, blank=True)
    target_model = models.CharField(max_length=60, blank=True)
    target_uuid = models.UUIDField(null=True, blank=True, db_index=True)
    target_label = models.CharField(max_length=255, blank=True)

    request_id = models.CharField(max_length=64, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("audit event")
        verbose_name_plural = _("audit events")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["target_app", "target_model", "target_uuid", "-created_at"],
                         name="audit_target_idx"),
            models.Index(fields=["actor", "-created_at"], name="audit_actor_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action} by {self.actor_label or 'system'}"

    def save(self, *args, **kwargs) -> None:
        """Refuse to rewrite history.

        The admin is configured readonly as well, but a model-level guard
        means no code path can quietly amend an event.
        """
        if self.pk is not None:
            raise ValueError("Audit events are append-only and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        raise ValueError("Audit events cannot be deleted.")
