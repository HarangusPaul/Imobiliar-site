from __future__ import annotations

from django.contrib import admin

from apps.access.models import Role, RoleAssignment


class RoleAssignmentInline(admin.TabularInline):
    model = RoleAssignment
    fk_name = "user"
    extra = 0
    autocomplete_fields = ("role", "granted_by")
    readonly_fields = ("created_at",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "priority", "is_system", "assignment_count")
    list_filter = ("is_system",)
    search_fields = ("code", "name", "description")
    ordering = ("priority", "code")
    readonly_fields = ("uuid", "created_at", "updated_at")

    @admin.display(description="Users")
    def assignment_count(self, obj: Role) -> int:
        return obj.assignments.count()

    def has_delete_permission(self, request, obj=None) -> bool:
        return not (obj and obj.is_system)


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "granted_by", "created_at")
    list_filter = ("role",)
    search_fields = ("user__phone_number", "user__first_name", "user__last_name", "role__code")
    autocomplete_fields = ("user", "role", "granted_by")
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "created_at", "updated_at")
