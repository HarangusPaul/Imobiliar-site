"""Django Admin registration for accounts.

Admin is the internal CRUD fallback while the React dashboard is being built.
It is configured to be genuinely usable - searchable, filterable, with
readonly audit columns - but it is not the destination UI and no workflow
logic is implemented here.
"""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, VerificationCode


class VerificationCodeInline(admin.TabularInline):
    model = VerificationCode
    extra = 0
    can_delete = False
    fields = ("purpose", "destination", "expires_at", "attempts", "consumed_at", "created_at")
    readonly_fields = fields
    ordering = ("-created_at",)

    def has_add_permission(self, request, obj=None) -> bool:
        return False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-created_at",)
    list_display = ("phone_number", "full_name", "email", "status", "is_phone_verified", "is_staff", "created_at")
    list_filter = ("status", "is_staff", "is_superuser", "is_active")
    search_fields = ("phone_number", "first_name", "last_name", "email", "uuid")
    readonly_fields = ("uuid", "created_at", "updated_at", "last_login", "phone_verified_at")
    inlines = [VerificationCodeInline]

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Profile"), {"fields": ("first_name", "last_name", "email")}),
        (_("Account state"), {"fields": ("status", "phone_verified_at", "is_active")}),
        (_("Admin access"), {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Audit"), {"fields": ("uuid", "last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    @admin.display(boolean=True, description=_("Phone verified"))
    def is_phone_verified(self, obj: User) -> bool:
        return obj.is_phone_verified

    @admin.display(description=_("Name"))
    def full_name(self, obj: User) -> str:
        return obj.full_name or "-"


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """Readonly: codes are issued and consumed by the domain, never by hand."""

    list_display = ("destination", "purpose", "expires_at", "attempts", "consumed_at", "created_at")
    list_filter = ("purpose",)
    search_fields = ("destination", "user__phone_number")
    autocomplete_fields = ("user",)
    ordering = ("-created_at",)
    readonly_fields = (
        "uuid", "user", "destination", "purpose", "code_hash",
        "expires_at", "attempts", "max_attempts", "consumed_at",
        "created_at", "updated_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
