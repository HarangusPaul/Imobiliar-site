import type { Metadata } from "next";

/**
 * `/account/profile` - name, email and contact preferences.
 *
 * The phone number renders readonly: it is the login identifier, and changing
 * it will require the verification flow.
 */

export const metadata: Metadata = { title: "Profile" };

export default function ProfilePage() {
  return (
    <div>
      <h1>Profile</h1>
      {/* <ProfileForm /> from features/account */}
    </div>
  );
}
