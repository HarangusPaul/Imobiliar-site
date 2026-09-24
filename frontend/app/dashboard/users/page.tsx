import type { Metadata } from "next";

/**
 * `/dashboard/users` - account administration.
 *
 * Requires the `users.manage` capability. Lists accounts with their roles,
 * status and verification state; the backend refuses the data to anyone else,
 * so an agent reaching this URL sees an error rather than a filtered list.
 */

export const metadata: Metadata = { title: "Users" };

export default function DashboardUsersPage() {
  return (
    <div>
      <h1>Users</h1>
      {/* <UserTable /> from features/dashboard */}
    </div>
  );
}
