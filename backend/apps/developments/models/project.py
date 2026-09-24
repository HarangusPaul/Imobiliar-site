"""Residential developments and their physical structure.

    Development
      └── Building
           └── Floor
                └── Unit

Why four levels rather than a flat unit table with a development pointer:

* A building has its own completion date, its own address and its own
  availability story. Buyers ask about building B, not about the project.
* Floors carry the floor plate: the layout drawing, the unit count, the
  orientation. Attaching that to each unit would duplicate it dozens of times.
* The public site navigates exactly this way (project, then building, then
  floor, then available apartments), so the model matches the journey.

A Unit is *inventory*. A Property is a *listing*. They are different things
with different lifecycles, which is why they are linked rather than merged -
see models/unit.py.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel, SoftDeleteModel


class DevelopmentStatus(models.TextChoices):
    PLANNED = "planned", _("Planned")
    UNDER_CONSTRUCTION = "under_construction", _("Under construction")
    COMPLETED = "completed", _("Completed")
    SOLD_OUT = "sold_out", _("Sold out")


class PublicationStatus(models.TextChoices):
    """Mirrors the property publication vocabulary on purpose.

    It is not imported from apps.properties: the two domains happen to share
    a vocabulary today, and coupling them would mean a change to listing
    workflow silently changing project workflow.
    """

    DRAFT = "draft", _("Draft")
    PENDING_REVIEW = "pending_review", _("Pending review")
    PUBLISHED = "published", _("Published")
    ARCHIVED = "archived", _("Archived")


class DevelopmentQuerySet(models.QuerySet):
    def published(self) -> "DevelopmentQuerySet":
        return self.filter(publication_status=PublicationStatus.PUBLISHED)


class Development(BaseModel, SoftDeleteModel):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    developer_name = models.CharField(
        max_length=180, blank=True, help_text=_("The company building the project.")
    )

    address = models.ForeignKey(
        "locations.Address", on_delete=models.PROTECT, related_name="developments"
    )

    status = models.CharField(
        max_length=24, choices=DevelopmentStatus.choices,
        default=DevelopmentStatus.PLANNED, db_index=True,
    )
    publication_status = models.CharField(
        max_length=20, choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT, db_index=True,
    )

    estimated_completion = models.DateField(null=True, blank=True)
    cover_image = models.ForeignKey(
        "media.MediaAsset", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cover_for_developments",
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name="managed_developments",
    )

    is_featured = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    objects = DevelopmentQuerySet.as_manager()
    all_objects = models.Manager.from_queryset(DevelopmentQuerySet)()

    class Meta:
        verbose_name = _("development")
        verbose_name_plural = _("developments")
        ordering = ["-is_featured", "name"]
        indexes = [models.Index(fields=["publication_status", "status"])]

    def __str__(self) -> str:
        return self.name


class Building(BaseModel):
    development = models.ForeignKey(
        Development, on_delete=models.CASCADE, related_name="buildings"
    )
    name = models.CharField(max_length=120, help_text=_("Building A, Tower 2, and so on."))
    code = models.CharField(max_length=30, blank=True)

    address = models.ForeignKey(
        "locations.Address", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="buildings",
        help_text=_("Only when the building differs from the project address."),
    )

    floors_above_ground = models.PositiveSmallIntegerField(default=0)
    floors_below_ground = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=24, choices=DevelopmentStatus.choices, default=DevelopmentStatus.PLANNED
    )
    estimated_completion = models.DateField(null=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _("building")
        verbose_name_plural = _("buildings")
        ordering = ["development", "sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["development", "name"], name="unique_building_name_per_development"
            )
        ]

    def __str__(self) -> str:
        return f"{self.development.name} - {self.name}"


class Floor(BaseModel):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="floors")
    level = models.SmallIntegerField(
        help_text=_("0 is ground floor; negative levels are below ground.")
    )
    name = models.CharField(
        max_length=60, blank=True, help_text=_("Optional label, e.g. Penthouse level.")
    )
    unit_count = models.PositiveSmallIntegerField(
        default=0, help_text=_("Planned units on this level.")
    )
    floor_plan = models.ForeignKey(
        "media.MediaAsset", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="floor_plan_for_floors",
        help_text=_("The floor plate drawing, stored via apps.media."),
    )

    class Meta:
        verbose_name = _("floor")
        verbose_name_plural = _("floors")
        ordering = ["building", "level"]
        constraints = [
            models.UniqueConstraint(fields=["building", "level"], name="unique_level_per_building")
        ]

    def __str__(self) -> str:
        return f"{self.building} - level {self.level}"
