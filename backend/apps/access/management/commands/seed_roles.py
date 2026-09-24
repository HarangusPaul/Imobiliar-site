"""Create the system roles. Safe to run repeatedly."""

from django.core.management.base import BaseCommand

from apps.access.models import Role
from apps.access.services.assignment import ensure_system_roles


class Command(BaseCommand):
    help = "Create or refresh the seeded product roles (client, agent, staff)."

    def handle(self, *args, **options) -> None:
        ensure_system_roles()
        for role in Role.objects.filter(is_system=True).order_by("priority"):
            self.stdout.write(
                self.style.SUCCESS(f"  {role.code:<10} {len(role.permissions)} capabilities")
            )
