# features/account

The signed-in user's own area.

| File | Responsibility |
|---|---|
| `api.ts` | profile read/update; the client's own submitted requests |
| `types.ts` | profile shapes (re-exports `Account` from `types/`) |
| `components/ProfileForm.tsx` | name, email, contact preferences |
| `components/AccountNav.tsx` | the account section sidebar |
| `components/RequestHistory.tsx` | enquiries this account has sent |
| `components/SavedPropertyList.tsx` | **deferred** |
| `components/SavedSearchList.tsx` | **deferred** |

## Deferred modules

Saved properties, saved searches and alerts have no backend endpoints in this
phase. The pages exist (see `app/(client)/account/`) and render an explicit
"coming soon" state rather than being hidden, so the information architecture
is settled now and only the data arrives later.

When the endpoints land, they belong in this feature's `api.ts`. No route
changes and no new top-level folder.

## Phone number

The phone number is the login identifier and cannot be edited from the profile
form in this phase. Changing it will require the verification flow
(`VerificationPurpose.PHONE_CHANGE` already exists in `apps/accounts`), which
is why the field renders readonly instead of being absent.
