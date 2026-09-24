"""Test settings.

Deliberately identical to ``local`` in wiring: tests exercise the same console
and local-filesystem implementations the developer runs, so a passing suite
says something true about the default configuration.
"""

import tempfile

from config.settings.base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-only-key"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

LOCAL_STORAGE_ROOT = tempfile.mkdtemp(prefix="imobiliar-test-media-")

LOGGING = {"version": 1, "disable_existing_loggers": True, "root": {"handlers": []}}
