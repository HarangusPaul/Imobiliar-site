import type { Metadata } from "next";

import { AuthCardHead, AuthShell, SocialButtons } from "@/features/auth/components/AuthShell";
import { RegisterForm } from "@/features/auth/components/RegisterForm";

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
    <AuthShell
      eyebrow="Join Monument"
      title="Find a place worth living in."
      text="Save homes you love, book private viewings and get first look at new listings before they go public."
      feature={{
        location: "Hudson Valley, New York",
        name: "Aster Ridge",
        note: "New this week",
        image: "/images/listings/aster-ridge.jpg",
      }}
    >
      <AuthCardHead
        title="Create your account"
        subtitle="It takes a minute. You can add your preferences later."
      />
      <SocialButtons />
      <RegisterForm />
    </AuthShell>
  );
}
