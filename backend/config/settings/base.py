"""Shared Django configuration.

``config`` is the composition root: it is the only layer allowed to know both
that ``apps`` exist and that ``services`` exist. It wires them together and
otherwise contains no logic.
"""

from __future__ import annotations

from pathlib import Path

import environ

from core.contracts.registry import ANALYTICS, NOTIFICATIONS, STORAGE, VERIFICATION
from services import registry as service_registry

BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-development-key")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# --- Applications ----------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
]

# Ordered roughly by dependency depth so migrations read sensibly.
LOCAL_APPS = [
    "apps.accounts",
    "apps.access",
    "apps.subscriptions",
    "apps.locations",
    "apps.properties",
    "apps.developments",
    "apps.media",
    "apps.leads",
    "apps.audit",
    "apps.content",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "core.middleware.RequestIDMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "config" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Database --------------------------------------------------------------

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL", default="postgres://imobiliar:imobiliar@localhost:5432/imobiliar"
    )
}
DATABASES["default"]["ATOMIC_REQUESTS"] = False  # transactions are opened by app services
DATABASES["default"]["CONN_MAX_AGE"] = 60

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Authentication --------------------------------------------------------

# Declared before the first migration. The identifier is a phone number.
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = ["apps.accounts.backends.PhoneNumberBackend"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation --------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Bucharest"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "var" / "static"

# --- Django REST Framework -------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Closed by default: every view states its own access requirements.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "core.api.pagination.DefaultPageNumberPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "EXCEPTION_HANDLER": "core.api.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {"anon": "120/hour", "lead-submit": "10/hour"},
    "UNAUTHENTICATED_USER": "django.contrib.auth.models.AnonymousUser",
}

# --- Pluggable service implementations -------------------------------------
# The single place where "which implementation is active" is decided.
# core.contracts.registry resolves these dotted paths lazily at call time,
# which is what keeps apps free of any import edge into services.

SERVICE_PROVIDERS = {
    NOTIFICATIONS: service_registry.resolve(NOTIFICATIONS, env("SERVICE_NOTIFICATIONS", default=None)),
    VERIFICATION: service_registry.resolve(VERIFICATION, env("SERVICE_VERIFICATION", default=None)),
    STORAGE: service_registry.resolve(STORAGE, env("SERVICE_STORAGE", default=None)),
    ANALYTICS: service_registry.resolve(ANALYTICS, env("SERVICE_ANALYTICS", default=None)),
}

LOCAL_STORAGE_ROOT = env("LOCAL_STORAGE_ROOT", default=str(BASE_DIR / "var" / "media"))
LOCAL_STORAGE_BASE_URL = env("LOCAL_STORAGE_BASE_URL", default="/media/")

# --- Domain policy knobs ---------------------------------------------------
# Values are configuration; the rules that consume them live in their apps.

ACCOUNTS_OTP_TTL_SECONDS = env.int("ACCOUNTS_OTP_TTL_SECONDS", default=300)
ACCOUNTS_OTP_MAX_ATTEMPTS = env.int("ACCOUNTS_OTP_MAX_ATTEMPTS", default=5)
ACCOUNTS_OTP_CODE_LENGTH = env.int("ACCOUNTS_OTP_CODE_LENGTH", default=6)
ACCOUNTS_DEFAULT_PHONE_PREFIX = env("ACCOUNTS_DEFAULT_PHONE_PREFIX", default="+40")

# --- Logging ---------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "core.logging.RequestIDFilter"}},
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s %(name)s [req:%(request_id)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "standard",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.db.backends": {"level": "WARNING", "handlers": ["console"], "propagate": False},
    },
}
