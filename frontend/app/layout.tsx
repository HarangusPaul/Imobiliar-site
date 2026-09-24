import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

/**
 * The root layout holds `<html>` and `<body>` and nothing else.
 *
 * It deliberately renders no header, footer or navigation: the four route
 * groups below it have genuinely different chrome, and each mounts its own
 * shell. Putting a site header here would force the dashboard and the login
 * page to undo it.
 */

export const metadata: Metadata = {
  title: {
    default: "Imobiliar",
    template: "%s | Imobiliar",
  },
  description: "Properties, residential developments and apartments.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ro">
      <body>{children}</body>
    </html>
  );
}
