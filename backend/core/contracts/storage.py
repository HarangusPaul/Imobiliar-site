"""File storage contract.

``apps/media`` owns metadata: what a file is, what it belongs to, its
category, alt text and ordering. It never performs I/O. An implementation of
this contract owns the bytes and the key namespace.

Binary content is never stored in PostgreSQL — only the ``key`` returned here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import BinaryIO, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class StoredFile:
    """The durable handle ``apps/media`` persists."""

    key: str  # opaque storage path/identifier
    size: int
    content_type: str
    checksum: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


class StorageError(Exception):
    """Raised by implementations when an I/O operation cannot complete."""


@runtime_checkable
class FileStorageService(Protocol):
    """Implemented in ``services/storage/``."""

    def save(self, *, namespace: str, filename: str, stream: BinaryIO, content_type: str) -> StoredFile:
        """Persist a stream and return its durable handle.

        ``namespace`` is a caller-chosen logical folder (``properties``,
        ``developments/units``, ``documents``) used to keep keys organised.
        """

    def open(self, key: str) -> BinaryIO: ...

    def delete(self, key: str) -> None: ...

    def exists(self, key: str) -> bool: ...

    def url(self, key: str) -> str:
        """Return a retrievable URL for the stored object."""
