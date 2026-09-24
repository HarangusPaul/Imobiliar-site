"""Development verification adapter: prints the code to the log.

It receives a code that ``apps/accounts`` generated, hashed and stored with an
expiry. This adapter never generates, validates or expires anything.
"""

from __future__ import annotations

import logging

from core.contracts.verification import (
    VerificationChannel,
    VerificationDispatchResult,
    VerificationRequest,
)
from core.security import mask_phone

logger = logging.getLogger("services.verification")


class ConsoleVerificationService:
    """Satisfies ``core.contracts.verification.VerificationService``."""

    supported_channels = frozenset({VerificationChannel.SMS, VerificationChannel.WHATSAPP})

    def supports(self, channel: VerificationChannel) -> bool:
        return channel in self.supported_channels

    def dispatch(self, request: VerificationRequest) -> VerificationDispatchResult:
        if not self.supports(request.channel):
            return VerificationDispatchResult(
                dispatched=False, error=f"Unsupported channel: {request.channel}"
            )

        logger.warning(
            "verification.dispatch (DEVELOPMENT ONLY - the code is logged in clear)\n"
            "  channel : %s\n"
            "  to      : %s\n"
            "  purpose : %s\n"
            "  code    : %s\n"
            "  expires : in %ss",
            request.channel,
            mask_phone(request.destination),
            request.purpose,
            request.code,
            request.ttl_seconds,
        )
        return VerificationDispatchResult(dispatched=True, reference="console")
