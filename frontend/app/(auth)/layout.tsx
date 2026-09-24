import type { ReactNode } from "react";

/**
 * Auth route group.
 *
 * `/login` and `/register` render without site navigation - a centred card and
 * nothing else. That is the reason they are their own group rather than pages
 * inside `(public)`.
 */

export default function AuthLayout({ children }: { children: ReactNode }) {
  return <main>{/* <AuthShell> */}{children}</main>;
}
