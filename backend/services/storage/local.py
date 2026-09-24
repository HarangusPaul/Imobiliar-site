"""Local filesystem storage adapter.

Owns bytes and key layout. It has no idea that a file is a property gallery
image, a floor plan or a legal document - ``apps/media`` owns that meaning and
passes only a neutral ``namespace``.
"""

from __future__ import annotations

import hashlib
import logging
import shutil
import uuid
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from django.conf import settings
from django.utils.text import get_valid_filename

from core.contracts.storage import StorageError, StoredFile

logger = logging.getLogger("services.storage")

_CHUNK = 64 * 1024


class LocalFileStorageService:
    """Satisfies ``core.contracts.storage.FileStorageService``."""

    def __init__(self) -> None:
        self.root = Path(settings.LOCAL_STORAGE_ROOT).resolve()
        self.base_url = str(settings.LOCAL_STORAGE_BASE_URL).rstrip("/") + "/"
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self, *, namespace: str, filename: str, stream: BinaryIO, content_type: str
    ) -> StoredFile:
        safe_name = get_valid_filename(Path(filename).name) or "file"
        # A random prefix keeps keys collision-free and non-enumerable.
        key = str(PurePosixPath(self._safe_namespace(namespace)) / f"{uuid.uuid4().hex}-{safe_name}")
        destination = self._absolute(key)
        destination.parent.mkdir(parents=True, exist_ok=True)

        digest = hashlib.sha256()
        size = 0
        try:
            with destination.open("wb") as target:
                while chunk := stream.read(_CHUNK):
                    digest.update(chunk)
                    size += len(chunk)
                    target.write(chunk)
        except OSError as exc:
            destination.unlink(missing_ok=True)
            raise StorageError(f"Could not write {key!r}.") from exc

        logger.info("storage.save key=%s size=%s", key, size)
        return StoredFile(
            key=key, size=size, content_type=content_type, checksum=digest.hexdigest()
        )

    def open(self, key: str) -> BinaryIO:
        path = self._absolute(key)
        if not path.is_file():
            raise StorageError(f"No stored object for key {key!r}.")
        return path.open("rb")

    def delete(self, key: str) -> None:
        self._absolute(key).unlink(missing_ok=True)
        logger.info("storage.delete key=%s", key)

    def exists(self, key: str) -> bool:
        return self._absolute(key).is_file()

    def url(self, key: str) -> str:
        return f"{self.base_url}{key.lstrip('/')}"

    def purge_namespace(self, namespace: str) -> None:
        """Development convenience for resetting fixtures."""
        shutil.rmtree(self._absolute(self._safe_namespace(namespace)), ignore_errors=True)

    @staticmethod
    def _safe_namespace(namespace: str) -> str:
        parts = [get_valid_filename(p) for p in PurePosixPath(namespace).parts if p not in ("/", "..")]
        return str(PurePosixPath(*parts)) if parts else "misc-namespace"

    def _absolute(self, key: str) -> Path:
        candidate = (self.root / key).resolve()
        # Refuse anything that escapes the storage root via traversal.
        if not candidate.is_relative_to(self.root):
            raise StorageError(f"Refusing to access {key!r} outside the storage root.")
        return candidate
