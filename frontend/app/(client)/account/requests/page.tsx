import type { Metadata } from "next";

/**
 * `/account/requests` - enquiries this account has sent.
 *
 * Reads leads scoped to the signed-in user. The client sees their own message
 * and its status, never the internal assignment or notes.
 */

export const metadata: Metadata = { title: "My requests" };

export default function RequestsPage() {
  return (
    <div>
      <h1>My requests</h1>
      {/* <RequestHistory /> from features/account */}
    </div>
  );
}
