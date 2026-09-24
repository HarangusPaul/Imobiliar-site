# features/leads

Contact and enquiry forms, and the staff inbox.

| File | Responsibility |
|---|---|
| `api.ts` | submit a lead; read the dashboard inbox |
| `types.ts` | submission, receipt and inbox row shapes |
| `schema.ts` | form validation |
| `components/ContactForm.tsx` | the general contact page form |
| `components/PropertyEnquiryForm.tsx` | prefilled from a listing |
| `components/DevelopmentEnquiryForm.tsx` | prefilled from a project |
| `components/LeadTable.tsx` | dashboard inbox list |
| `components/LeadStatusBadge.tsx` | status pill |
| `components/LeadTimeline.tsx` | notes and history on the detail page |

## One form, three entry points

All three forms post to the same endpoint and differ only in which subject they
prefill. Keeping them as separate thin components beats one component with a
mode prop, because each has different copy and different required context.

## What comes back

A public submission returns `{ id, status, created_at }` and nothing else. The
form must not expect to learn which agent received the lead - that is internal
state, and the backend deliberately withholds it.

## Spam handling

The `website` field is a honeypot: hidden in the layout, and a submission that
fills it is rejected server-side. Keep it rendered and keep it unlabelled.
