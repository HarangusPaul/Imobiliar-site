"""The custom user model. Declared before the first migration, as required.

Identity is the phone number. There is no username field, and email is
optional contact data rather than a credential.

What this model deliberately does *not* own:
  * product roles -> ``apps.access`` (``RoleAssignment``)
  * entitlements  -> ``apps.subscriptions``
  * agent profile / listing ownership -> ``apps.properties``

``is_staff`` remains only because Django Admin needs it to gate the fallback
CRUD surface. It is not the product's notion of "staff"; that is a role code
in ``apps.access``.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import UUIDModel
from core.validation import normalize_phone


class AccountStatus(models.TextChoices):
    """Lifecycle of an account, independent of ``is_active``.

    ``is_active`` is Django's hard on/off switch used by the auth backend.
    ``status`` is the business-visible state the dashboard displays.
    """

    PENDING = "pending", _("Pending verification")
    ACTIVE = "active", _("Active")
    SUSPENDED = "suspended", _("Suspended")
    CLOSED = "closed", _("Closed")


class UserManager(BaseUserManager):
    """Creates users keyed by a normalised phone number."""

    use_in_migrations = True

    def _create_user(self, phone_number: str, password: str | None, **extra) -> "User":
        if not phone_number:
            raise ValueError("A phone number is required to create a user.")
        prefix = getattr(settings, "ACCOUNTS_DEFAULT_PHONE_PREFIX", "+40")
        phone_number = normalize_phone(phone_number, default_country_prefix=prefix)
        user = self.model(phone_number=phone_number, **extra)
        user.set_password(password)
        user.full_clean(exclude=["password"])
        user.save(using=self._db)
        return user

    def create_user(self, phone_number: str, password: str | None = None, **extra) -> "User":
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra)

    def create_superuser(self, phone_number: str, password: str, **extra) -> "User":
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("status", AccountStatus.ACTIVE)
        extra.setdefault("phone_verified_at", timezone.now())
        if not extra["is_staff"] or not extra["is_superuser"]:
            raise ValueError("A superuser must have is_staff=True and is_superuser=True.")
        return self._create_user(phone_number, password, **extra)


class User(UUIDModel, AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_("Stored in E.164 form. This is the login identifier."),
    )
    first_name = models.CharField(_("first name"), max_length=80, blank=True)
    last_name = models.CharField(_("last name"), max_length=80, blank=True)
    email = models.EmailField(_("email"), blank=True)

    status = models.CharField(
        max_length=16, choices=AccountStatus.choices, default=AccountStatus.PENDING, db_index=True
    )
    phone_verified_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False, help_text=_("Grants access to Django Admin, the internal CRUD fallback.")
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.phone_number

    def clean(self) -> None:
        super().clean()
        prefix = getattr(settings, "ACCOUNTS_DEFAULT_PHONE_PREFIX", "+40")
        self.phone_number = normalize_phone(self.phone_number, default_country_prefix=prefix)
        self.email = self.email.strip().lower()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self) -> str:
        return self.full_name or self.phone_number

    def get_short_name(self) -> str:
        return self.first_name or self.phone_number

    @property
    def is_phone_verified(self) -> bool:
        return self.phone_verified_at is not None

    @property
    def can_authenticate(self) -> bool:
        """Business rule: which account states may hold a session.

        Phone verification is not required to log in yet - it becomes a
        precondition when OTP is switched on, and this is the single place
        that changes.
        """
        return self.is_active and self.status in {AccountStatus.PENDING, AccountStatus.ACTIVE}
