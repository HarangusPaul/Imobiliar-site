"""Deferred work owned by the subscriptions domain."""

from __future__ import annotations

import logging

from core.tasks import Task

from apps.subscriptions.services.lifecycle import expire_due_subscriptions

logger = logging.getLogger(__name__)


class ExpireDueSubscriptionsTask(Task):
    name = "subscriptions.expire_due"

    def run(self) -> None:
        count = expire_due_subscriptions()
        if count:
            logger.info("subscriptions.expired count=%s", count)


expire_due_subscriptions_task = ExpireDueSubscriptionsTask()
