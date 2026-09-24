import type { Metadata } from "next";

/**
 * `/dashboard/leads/[id]` - one enquiry.
 *
 * Shows the message, the subject listing or project, the status timeline and
 * the notes. Status changes go through the backend workflow service, which
 * enforces the transition table - the UI only offers the moves that are legal
 * from the current state.
 */

export const metadata: Metadata = { title: "Lead" };

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function LeadDetailPage({ params }: PageProps) {
  const { id } = await params;

  return (
    <div>
      <h1>Lead</h1>
      <p>{id}</p>
      {/* <LeadTimeline /> and the assignment control */}
    </div>
  );
}
