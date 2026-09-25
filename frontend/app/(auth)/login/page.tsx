import type { Metadata, Route } from "next";

import { AuthCardHead, AuthShell, SocialButtons } from "@/features/auth/components/AuthShell";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { routes } from "@/lib/constants/routes";

/**
 * `/login` - phone number and password.
 *
 * Signed-in visitors never reach this page: `middleware.ts` redirects them.
 * The `?next=` parameter carries the page they were trying to open.
 */

export const metadata: Metadata = { title: "Log in" };

interface PageProps {
  searchParams: Promise<{ next?: string | string[] }>;
}

/** Only same-site paths, so `?next=` cannot send anyone to another origin. */
function safeNext(value: string | string[] | undefined): Route {
  const next = Array.isArray(value) ? value[0] : value;
  return (next && next.startsWith("/") && !next.startsWith("//") ? next : routes.home) as Route;
}

export default async function LoginPage({ searchParams }: PageProps) {
  const { next } = await searchParams;

  return (
    <AuthShell
      eyebrow="Members"
      title="Welcome back to the collection."
      text="Pick up where you left off. Your saved homes, viewings and advisor notes are waiting."
      feature={{
        location: "Costa Brava, Spain",
        name: "Casa del Acantilado",
        note: "Featured this month",
        image: "/images/home/hero.jpg",
      }}
    >
      <AuthCardHead
        title="Log in"
        subtitle="Use your phone number or continue with an account you already have."
      />
      <SocialButtons />
      <LoginForm next={safeNext(next)} />
    </AuthShell>
  );
}
