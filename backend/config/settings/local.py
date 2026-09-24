"""Local development settings."""

from config.settings.base import *  # noqa: F403
from config.settings.base import INSTALLED_APPS, REST_FRAMEWORK

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# The Next.js dev server talks to this API cross-origin.
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]

# Browsable API is convenient while the dashboard does not exist yet.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

INSTALLED_APPS = [*INSTALLED_APPS]
