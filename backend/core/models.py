"""Domain-neutral abstract model bases.

Nothing here may know about properties, leads, roles or subscriptions. These
are structural primitives only: identity, time, and lifecycle.

Identity decision
-----------------
Rows keep a ``BigAutoField`` primary key for index locality and cheap foreign
keys, and expose a separate indexed ``uuid`` as the *public* identifier used in
APIs and in the dashboard. Sequential integers are never exposed publicly.
"""

from __future__ import annotations

import uuid as uuid_lib

from django.db import models
from django.utils import timezone


class UUIDModel(models.Model):
    """Adds a stable, non-guessable public identifier."""

    uuid = models.UUIDField(
        default=uuid_lib.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="Public identifier. Safe to expose in APIs and URLs.",
    )

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """Adds creation/modification bookkeeping."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimestampedModel):
    """The default base for domain entities: public UUID + timestamps."""

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """Queryset that understands the soft-delete marker."""

    def alive(self) -> SoftDeleteQuerySet:
        return self.filter(deleted_at__isnull=True)

    def dead(self) -> SoftDeleteQuerySet:
        return self.filter(deleted_at__isnull=False)

    def soft_delete(self) -> int:
        return self.update(deleted_at=timezone.now())


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Default manager that hides soft-deleted rows.

    ``all_objects`` on the concrete model should be declared when a domain
    genuinely needs to reach deleted rows (e.g. audit reconciliation).
    """

    def get_queryset(self) -> SoftDeleteQuerySet:
        return super().get_queryset().alive()


class SoftDeleteModel(models.Model):
    """Opt-in soft deletion.

    Only inherit this where the domain has a real need to retain rows after
    removal (properties, media, leads). Do not apply it reflexively.
    """

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True, editable=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self) -> None:
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])
