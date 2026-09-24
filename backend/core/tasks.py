"""Base class for deferred/background work.

No broker is configured in this phase. Tasks run inline on commit, which is
correct for local development and keeps the call sites honest: app code must
already treat a task as fire-and-forget, so introducing a real queue later is
a change to this module only, not to any domain app.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from django.db import transaction

from core.logging import get_request_id

logger = logging.getLogger(__name__)


class Task(ABC):
    """A named unit of deferred work.

    Subclasses live in ``apps/<domain>/tasks.py`` and own their business
    meaning. This base owns only scheduling semantics and error containment.
    """

    name: str = "task"

    @abstractmethod
    def run(self, **kwargs: Any) -> None:
        """Perform the work. Must be idempotent."""

    def enqueue(self, **kwargs: Any) -> None:
        """Schedule the task to run after the current transaction commits.

        Running on commit means a task never observes a half-written or
        rolled-back domain state.
        """
        request_id = get_request_id()
        transaction.on_commit(lambda: self._execute(request_id=request_id, **kwargs))

    def _execute(self, *, request_id: str, **kwargs: Any) -> None:
        logger.info("task.start", extra={"task": self.name, "request_id": request_id})
        try:
            self.run(**kwargs)
        except Exception:
            # A failed side effect must never corrupt the originating request.
            logger.exception("task.failed", extra={"task": self.name, "request_id": request_id})
        else:
            logger.info("task.done", extra={"task": self.name, "request_id": request_id})
