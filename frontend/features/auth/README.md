# features/auth

Registration, login and logout.

| File | Responsibility |
|---|---|
| `api.ts` | the three auth requests |
| `schema.ts` | client-side form schemas |
| `components/LoginForm.tsx` | phone + password form |
| `components/RegisterForm.tsx` | account creation form |
| `components/LogoutButton.tsx` | ends the session and revalidates |
| `components/VerifyCodeForm.tsx` | **deferred** - the OTP step, UI only |

## How the session works

Authentication is a Django session cookie. The browser holds no token: requests
go to `/api/backend/*` on this origin and Next.js proxies them, so the cookie
is first-party and `lib/api` needs no auth header logic at all.

After a successful login the auth action revalidates the account cache and
redirects. `middleware.ts` checks only for cookie *presence*; the backend
decides who the caller actually is on every request.

## About OTP

The backend already models verification codes (`apps/accounts`) with no
delivery channel configured. `VerifyCodeForm` is scaffolded for that step but
is not wired into the registration flow in this phase. When a channel is
enabled server-side, this feature gains one screen - the login flow, the
session model and the route structure do not change.
