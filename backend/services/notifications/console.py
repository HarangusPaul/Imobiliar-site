"""Development notification adapter: writes messages to the log.

Delivery only. It does not know what a lead is, who an agent is, or when a
message should be sent - those decisions were already made by the calling
domain app before the message reached this object.
"""

from __future__ import annotations

import logging

from core.contracts.notification import (
    NotificationChannel,
    NotificationMessage,
    NotificationResult,
)
from core.security import mask_phone

logger = logging.getLogger("services.notifications")


class ConsoleNotificationService:
    """Satisfies ``core.contracts.notification.NotificationService``."""

    supported_channels = frozenset(NotificationChannel)

    def supports(self, channel: NotificationChannel) -> bool:
        return channel in self.supported_channels

    def send(self, message: NotificationMessage) -> NotificationResult:
        if not self.supports(message.channel):
            return NotificationResult(
                delivered=False, error=f"Unsupported channel: {message.channel}"
            )

        destination = message.recipient.address
        if message.channel is NotificationChannel.SMS:
            destination = mask_phone(destination)

        logger.info(
            "notification.send\n"
            "  channel : %s\n"
            "  kind    : %s\n"
            "  to      : %s %s\n"
            "  subject : %s\n"
            "  body    : %s",
            message.channel,
            message.kind,
            destination,
            message.recipient.display_name,
            message.subject,
            message.body,
        )
        return NotificationResult(delivered=True, reference="console")
