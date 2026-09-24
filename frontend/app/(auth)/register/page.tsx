import type { Metadata } from "next";

/**
 * `/register` - account creation.
 *
 * The identifier is a phone number; there is no username. The account is
 * created in a pending state and can sign in immediately. When verification is
 * switched on server-side, a code step joins this flow without changing the
 * route structure.
 */

export const metadata: Metadata = { title: "Create an account" };

export default function RegisterPage() {
  return (
    <div>
      <h1>Create an account</h1>
      {/* <RegisterForm /> from features/auth */}
    </div>
  );
}
