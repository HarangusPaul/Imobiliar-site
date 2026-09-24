"""SEO metadata foundations.

This app is intentionally small. It is not a CMS and must not become one in
this phase.

What it does own: the SEO fields that every public URL needs, expressed once
as an abstract mixin so properties, developments and any future page type
share the same vocabulary and the same defaults. A property listing is a page
with a title and a description whether or not a CMS ever exists.

PresentationPage is a minimal placeholder for the handful of static pages the
public site needs (about, contact, terms). It stores a title, a slug and a
body. When richer content modelling is genuinely required, it will be designed
then - not guessed at now.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class SEOMetadataMixin(models.Model):
    """Reusable SEO fields.

    Every field is optional and falls back to the object's own content, so
    nothing has to be filled in twice for a page to be indexable.
    """

    seo_title = models.CharField(
        max_length=70, blank=True, help_text=_("Overrides the page title in search results.")
    )
    seo_description = models.CharField(
        max_length=160, blank=True, help_text=_("Meta description. Roughly 150 characters.")
    )
    seo_keywords = models.CharField(max_length=255, blank=True)
    og_image = models.ForeignKey(
        "media.MediaAsset",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text=_("Social sharing image. Falls back to the cover image."),
    )
    noindex = models.BooleanField(
        default=False, help_text=_("Ask search engines not to index this page.")
    )
    canonical_path = models.CharField(
        max_length=255, blank=True, help_text=_("Canonical path when this page duplicates another.")
    )

    class Meta:
        abstract = True

    def resolved_seo_title(self, fallback: str = "") -> str:
        return self.seo_title or fallback

    def resolved_seo_description(self, fallback: str = "") -> str:
        return self.seo_description or fallback[:160]


class PresentationPage(BaseModel, SEOMetadataMixin):
    """A static company page. Deliberately minimal."""

    slug = models.SlugField(max_length=140, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    is_published = models.BooleanField(default=False, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _("presentation page")
        verbose_name_plural = _("presentation pages")
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return self.title
