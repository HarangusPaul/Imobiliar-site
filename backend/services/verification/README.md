# services/verification

Delivers a verification code to a destination. That is the entire job.

**Contract:** `core.contracts.verification.VerificationService`

## Ownership split

| Concern | Owner |
|---|---|
| Generating the code | `apps/accounts` (using `core.security`) |
| Hashing and storing it | `apps/accounts` |
| Expiry window | `apps/accounts` |
| Attempt counting and lockout | `apps/accounts` |
| Deciding that a submitted code is correct | `apps/accounts` |
| Resend throttling policy | `apps/accounts` |
| Putting the code in front of the user | **here** |

`console.py` logs the code in clear, which is why it belongs to development
settings only. It is the sole implementation in this phase.

## Adding a real channel later

Implement the protocol in a new module, register it in `services/registry.py`,
and switch `SERVICE_VERIFICATION`. The user model, the verification-code state
machine and the auth endpoints stay untouched - that is precisely why this seam
exists.
