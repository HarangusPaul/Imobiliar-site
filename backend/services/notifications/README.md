# services/notifications

Delivers a message that a domain app has already composed and already decided
to send.

**Contract:** `core.contracts.notification.NotificationService`

## What lives here

- Transport adapters, and nothing else.
- `console.py` - logs the message. The only implementation in this phase.

## What must never live here

- Deciding *whether* a notification should happen. That is `apps/leads`
  (a new lead was assigned), `apps/accounts` (an account changed state), etc.
- Selecting recipients from domain data. The caller passes a
  `NotificationRecipient` holding a plain address.
- Message copy that encodes business rules. Rendering belongs to the app that
  owns the meaning of the message.
- Retry or escalation policy that depends on business state.

## Adding an implementation later

1. Add `services/notifications/<name>.py` implementing the protocol.
2. Register its dotted path in `services/registry.py`.
3. Point `SERVICE_NOTIFICATIONS` at it.

No file under `apps/` changes.
