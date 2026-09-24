"""Django Admin for leads.

Status changes are exposed as actions routed through the workflow service, so
the transition table is enforced even here.
"""

from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from core.api.exceptions import DomainError

from apps.leads.models import Lead, LeadNote, LeadStatus
from apps.leads.services.workflow import change_status


class LeadNoteInline(admin.TabularInline):
    model = LeadNote
    extra = 1
    fields = ("body", "author", "is_system", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "kind", "status", "subject_label",
                    "assigned_to", "created_at")
    list_filter = ("status", "kind", "contact_preference", "assigned_to")
    search_fields = ("full_name", "phone_number", "email", "message",
                     "property__reference_code", "development__name")
    autocomplete_fields = ("property", "development", "unit", "user", "assigned_to")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("property", "development", "assigned_to")
    inlines = [LeadNoteInline]
    actions = ["mark_contacted", "mark_spam"]

    readonly_fields = ("uuid", "request_id", "source_path", "created_at", "updated_at",
                       "assigned_at", "first_response_at", "closed_at")

    fieldsets = (
        (None, {"fields": ("kind", "status", "assigned_to", "assigned_at")}),
        (_("Contact"), {"fields": ("full_name", "phone_number", "email",
                                   "contact_preference", "preferred_time", "user")}),
        (_("Enquiry"), {"fields": ("message", "property", "development", "unit")}),
        (_("Handling"), {"fields": ("first_response_at", "closed_at")}),
        (_("Origin"), {"fields": ("source_path", "request_id")}),
        (_("Audit"), {"fields": ("uuid", "created_at", "updated_at")}),
    )

    @admin.display(description=_("About"))
    def subject_label(self, obj: Lead) -> str:
        return str(obj.subject) if obj.subject is not None else "-"

    @admin.action(description=_("Mark as contacted"))
    def mark_contacted(self, request, queryset) -> None:
        self._transition(request, queryset, LeadStatus.CONTACTED)

    @admin.action(description=_("Mark as spam"))
    def mark_spam(self, request, queryset) -> None:
        self._transition(request, queryset, LeadStatus.SPAM)

    def _transition(self, request, queryset, target: str) -> None:
        moved, blocked = 0, []
        for lead in queryset:
            try:
                change_status(lead, target=target, actor=request.user)
                moved += 1
            except DomainError as exc:
                blocked.append(f"{lead.full_name}: {exc.message}")
        if moved:
            self.message_user(request, f"{moved} lead(s) moved to {target}.", messages.SUCCESS)
        for problem in blocked:
            self.message_user(request, problem, messages.WARNING)


@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ("lead", "author", "is_system", "created_at")
    list_filter = ("is_system",)
    search_fields = ("body", "lead__full_name", "lead__phone_number")
    autocomplete_fields = ("lead", "author")
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "created_at", "updated_at")
