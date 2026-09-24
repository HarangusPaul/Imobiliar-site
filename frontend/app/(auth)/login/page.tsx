import type { Metadata } from "next";

/**
 * `/login` - phone number and password.
 *
 * Signed-in visitors never reach this page: `middleware.ts` redirects them.
 * The `?next=` parameter carries the page they were trying to open.
 */

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <div>
      <h1>Sign in</h1>
      {/* <LoginForm /> from features/auth */}
    </div>
  );
}
