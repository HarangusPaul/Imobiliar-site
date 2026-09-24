"""Product roles and their assignment to users.

Roles are *data*, not code. A role is a row with a code, and permissions are
rows attached to it. Adding a role later - regional_manager, developer_partner,
partner_agency - is an administrative act, not a code change scattered across
the project. That is the whole reason this app exists separately from
apps.accounts.

Roles are not subscriptions. A role says what kind of actor somebody is; a
subscription says what a paying account has bought. A client on a premium plan
is still the client role.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class DefaultRole(models.TextChoices):
    """Seed values only.

    Code must not branch on these constants beyond bootstrapping. Ask about a
    permission (see Role.permissions) rather than about a role code.
    """

    CLIENT = "client", _("Client")
    AGENT = "agent", _("Agent")
    STAFF = "staff", _("Staff")


class AccessArea(models.TextChoices):
    """Which API zone / UI surface a role may reach at all."""

    PUBLIC = "public", _("Public website")
    CLIENT = "client", _("Client account")
    DASHBOARD = "dashboard", _("Internal dashboard")
    INTERNAL = "internal", _("Restricted internal")


class Role(BaseModel):
    code = models.SlugField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    areas = models.JSONField(
        default=list,
        blank=True,
        help_text=_("AccessArea values this role may reach."),
    )
    permissions = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Dotted capability strings, e.g. properties.publish, leads.assign."),
    )

    is_system = models.BooleanField(
        default=False, help_text=_("System roles are seeded by the project and cannot be deleted.")
    )
    priority = models.PositiveSmallIntegerField(
        default=100, help_text=_("Lower wins when a single effective role must be chosen.")
    )

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ["priority", "code"]

    def __str__(self) -> str:
        return self.name

    def grants(self, permission: str) -> bool:
        return permission in self.permissions

    def can_reach(self, area: str) -> bool:
        return area in self.areas


class RoleAssignment(BaseModel):
    """Many-to-many with provenance.

    A through-model rather than a plain M2M because who granted a role and
    when is information the dashboard and apps.audit both need.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="role_assignments"
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="assignments")
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_role_assignments",
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("role assignment")
        verbose_name_plural = _("role assignments")
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], name="unique_user_role"),
        ]
        ordering = ["role__priority"]

    def __str__(self) -> str:
        return f"{self.user} = {self.role.code}"
