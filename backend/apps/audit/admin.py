"""Django Admin for audit events - strictly readonly.

Add, change and delete are all disabled. The list is searchable and filterable
because reading the trail is the entire point.
"""

from __future__ import annotations

import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "actor_label", "target_label", "request_id")
    list_filter = ("action", "target_app", "target_model")
    search_fields = ("action", "actor_label", "target_label", "request_id", "target_uuid")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("actor",)

    fields = ("action", "actor", "actor_label", "target_app", "target_model",
              "target_uuid", "target_label", "request_id", "metadata_pretty", "created_at")
    readonly_fields = fields

    @admin.display(description=_("Metadata"))
    def metadata_pretty(self, obj: AuditEvent) -> str:
        return format_html("<pre>{}</pre>", json.dumps(obj.metadata, indent=2, ensure_ascii=False))

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
