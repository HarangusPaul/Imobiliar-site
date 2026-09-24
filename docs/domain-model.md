# Domain model

## Overview

```
accounts.User ──< access.RoleAssignment >── access.Role
      │
      ├──< subscriptions.Subscription >── subscriptions.Plan
      │
      ├──< properties.Property   (as agent)
      └──< leads.Lead            (as assignee / as sender)

locations.Country ──< City ──< Neighborhood
                        └──< locations.Address
                                  │
                ┌─────────────────┴──────────────────┐
     properties.Property                  developments.Development
                                                     │
                                          developments.Building
                                                     │
                                          developments.Floor
                                                     │
                                          developments.Unit ──0..1── properties.Property
                                                     ^
                                          developments.UnitType

media.MediaAsset ──(generic)── Property, Development, Floor, UnitType, PresentationPage

leads.Lead ──0..1── Property / Development / Unit
leads.Lead ──< leads.LeadNote

audit.AuditEvent ── denormalised reference to any object
```

## Identity

Every domain entity carries a `BigAutoField` primary key and a separate
indexed `uuid`. Foreign keys and indexes use the integer; APIs expose only the
UUID, or a slug for public URLs. Sequential ids are never public.

## accounts

`User` has no username. `phone_number` is unique, stored in E.164, and is the
login identifier. `email` is optional contact data.

Two status concepts, deliberately separate: `is_active` is the hard on/off
switch used by the auth backend, and `status` is the business lifecycle the
dashboard displays (`pending`, `active`, `suspended`, `closed`). A new account
starts `pending` and can sign in; the same state becomes "awaiting
verification" the day OTP is enabled.

`VerificationCode` holds a keyed hash of the code, its expiry, attempt count
and consumption timestamp. The clear code is never stored. The hash is salted
with `purpose:destination`, so a code issued for one flow cannot be replayed in
another. Issuing a new code consumes the previous one, so exactly one code is
valid at a time.

## access

`Role` is a row: a code, a set of `permissions` (capability strings) and a set
of `areas` (which API zones it may reach). `RoleAssignment` is a through model
rather than a plain many-to-many because who granted a role and when is
information the dashboard and the audit trail both need.

Seeded roles: `client`, `agent`, `staff`. They are defaults, not a closed set.
Adding `partner_agency` means inserting a row, because nothing branches on a
role code: code asks `has_capability(user, Capability.X)`.

Capabilities union across roles - a user holding both `agent` and `staff` gets
both sets.

## subscriptions

`Plan` carries `entitlements` as data. `Subscription` links a user to a plan
with a status and a validity window.

**At most one subscription is current per user.** Granting a new one expires
the previous, so `has_entitlement` is never ambiguous. Users with no
subscription fall back to the plan marked `is_default`, so callers never need a
null case.

Roles and subscriptions are orthogonal. A staff member with no subscription
administers the platform; a client on the top plan is still a client.

No payment concept exists anywhere in this app.

## locations

`Country` > `City` > `Neighborhood`, all carrying optional coordinates.
`Address` is a shared table referenced by both properties and developments.

Address visibility is a property of the address (`is_exact_public`), not of
each listing, so the rule cannot drift between the two consumers.
`public_label` returns neighborhood and city; `full_label` returns the street.
Subscribers may see the exact address even when it is not public.

Coordinates are plain decimals. No GIS extension and no map integration in this
phase, but the columns exist from the first migration, so PostGIS is an
additive change rather than a data migration.

## properties

A listing has **three independent state axes**:

| Axis | Values | Question it answers |
|---|---|---|
| `publication_status` | draft, pending_review, published, archived | is it on the public site? |
| `availability_status` | available, reserved, sold, rented, unavailable | can it still be transacted? |
| `transaction_type` | sale, rent | is it for sale or for rent? |

Collapsing them into one status field is the usual mistake. A listing can be
published *and* reserved; it can be archived while still recorded as sold; a
rental and a sale share every publication rule.

Publication transitions are restricted by a table in `models/enums.py` and
enforced in `services/publishing.py`. Publishing also requires completeness: a
title, a short description, a price and a cover image. Archived cannot jump
straight back to published - it returns to draft first.

`Feature` (amenities) are rows, not boolean columns: the set grows with the
market, and a listings table with sixty booleans is unmaintainable. Features
carry `is_premium_filter`, which is how filtering becomes entitlement-gated
without the properties app knowing what a plan is.

`cover_image` is a denormalised pointer into `media`, so a 24-card grid costs
one join rather than twenty-four queries.

Indexes target the actual access patterns:

- `(publication_status, availability_status, -published_at)` - the public feed
- `(transaction_type, property_type, price)` - the dominant facet combination
- `(agent, publication_status)` - the agent dashboard

## developments

```
Development
  └── Building
       └── Floor
            └── Unit
```

Four levels, not a flat unit table, because each level owns real information:

- a **Building** has its own completion date, status and sometimes its own
  address; buyers ask about building B, not about the project;
- a **Floor** carries the floor plate - the layout drawing, the unit count, the
  orientation - which would otherwise be duplicated on every unit;
- the public site navigates exactly this way, so the model matches the journey.

`UnitType` is the repeated layout. The same two-room plan may occur on fifteen
floors; modelling it once stores the drawing, the area and the room count once.
A `Unit` may override any of it, and `effective_rooms` /
`effective_usable_area` resolve the inheritance.

### Unit vs Property - the key relationship

```
developments.Unit ──0..1── properties.Property
      (inventory)              (listing)
```

A **Unit** is inventory. Apartment 4B exists whether or not anyone is selling
it today, has a fixed area and layout, and belongs to its floor permanently.

A **Property** is a listing. It has marketing copy, a price that changes, a
publication workflow, a responsible agent, and it may be withdrawn and
relisted.

Separate tables joined by an optional `OneToOneField` gives:

- a development whose inventory is fully modelled while nothing is published;
- units sold internally that never appear on the public site;
- a listing archived without destroying the unit record;
- one place (`Unit.availability`) that stays true regardless of listing state.

Merging them would force every unit to carry listing machinery, and would turn
"which apartments are left in Building A" into a question about publication
status.

Consistency is maintained in `services/inventory.py`: changing unit
availability propagates to the linked listing, and a sold or withheld unit
cannot be linked to a public listing.

## media

`MediaAsset` stores metadata plus `file_key`, an opaque handle returned by the
storage contract. **No binary content is stored in PostgreSQL.**

Attachment is generic (content type + object id) rather than a foreign key per
owner, because media attaches to properties, developments, floors, unit types
and content pages, and that list will grow. `category` (gallery, cover, layout,
floor_plan, site_plan, document, certificate) drives which API surface exposes
a file; `PUBLIC_CATEGORIES` is the set a visitor may see without entitlement.

The app decides what a file *means*; `services/storage` owns the bytes. No
filesystem call appears anywhere under `apps/media`.

## leads

One table covers general contact, property enquiries and development
enquiries - they differ only in what they point at, and splitting them would
force the dashboard to merge three inboxes for nothing. `kind` plus three
nullable relations express the difference. A lead may reference a property, a
development, a unit, or nothing.

A lead is not a user. Most enquiries come from people without an account, so
contact details live on the row; `user` is filled in only when the sender was
signed in.

The status flow (`new`, `contacted`, `qualified`, `closed`, `spam`) is a table
in `services/workflow.py`. `spam` is terminal. A closed lead reopens only as
`qualified`. First contact stamps `first_response_at`, which is the number that
makes response time measurable.

`LeadNote` is the handling history, separate from `audit` because these entries
are the conversation staff actually read.

A property enquiry auto-assigns to the listing agent. That decision belongs to
`apps/leads`; delivering the resulting message is a contract call.

## audit

`AuditEvent` is append-only: no `updated_at`, no soft delete, `save()` refuses
to rewrite an existing row, `delete()` raises, and the admin disables add,
change and delete.

The target is stored denormalised - app label, model name, UUID and a text
label - rather than as a foreign key. A foreign key would cascade or protect; an
audit trail must survive the deletion of the thing it describes and still read
sensibly. The same applies to `actor_label`, copied onto the row so the record
stays meaningful after an account is removed.

`request_id` ties an event to the server log line and to every other event from
the same request.

## content

`SEOMetadataMixin` is an abstract set of SEO fields any page-like model can
inherit, with fallbacks to the object title and description.
`PresentationPage` is a minimal static-page model. Deliberately not a CMS.
