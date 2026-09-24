import type { Metadata } from "next";

/**
 * `/dashboard/roles` - roles and their capabilities.
 *
 * Roles are data, not code: a new role is a row with a set of capabilities and
 * accessible areas. This screen is what makes that promise real - adding
 * "partner agency" is an administrative act, not a deployment.
 *
 * Seeded system roles (client, agent, staff) can be edited but not deleted.
 */

export const metadata: Metadata = { title: "Roles" };

export default function DashboardRolesPage() {
  return (
    <div>
      <h1>Roles</h1>
      {/* <RoleEditor /> from features/dashboard */}
    </div>
  );
}
