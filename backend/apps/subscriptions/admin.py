from __future__ import annotations

from django.contrib import admin

from apps.subscriptions.models import Plan, Subscription


class SubscriptionInline(admin.TabularInline):
    """Attached to the user page so staff see entitlements in context."""

    model = Subscription
    extra = 0
    fields = ("plan", "status", "starts_at", "ends_at", "note")
    autocomplete_fields = ("plan",)
    readonly_fields = ("created_at",)
    ordering = ("-starts_at",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "price", "currency", "billing_period", "is_active", "is_default")
    list_filter = ("is_active", "is_default", "billing_period")
    search_fields = ("code", "name", "description")
    ordering = ("sort_order", "price")
    readonly_fields = ("uuid", "created_at", "updated_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "starts_at", "ends_at", "is_current")
    list_filter = ("status", "plan")
    search_fields = ("user__phone_number", "user__first_name", "user__last_name", "plan__code")
    autocomplete_fields = ("user", "plan")
    ordering = ("-starts_at",)
    readonly_fields = ("uuid", "created_at", "updated_at", "cancelled_at")

    @admin.display(boolean=True, description="Current")
    def is_current(self, obj: Subscription) -> bool:
        return obj.is_current
