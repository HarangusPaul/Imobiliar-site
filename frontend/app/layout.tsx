import type { Metadata } from "next";
import { Arimo, Inter } from "next/font/google";
import type { ReactNode } from "react";

import "./globals.css";

const inter = Inter({ subsets: ["latin", "latin-ext"], variable: "--font-inter" });
const arimo = Arimo({
  subsets: ["latin", "latin-ext"],
  weight: ["700"],
  variable: "--font-arimo",
});

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
    <html lang="ro" className={`${inter.variable} ${arimo.variable}`}>
      <body>{children}</body>
    </html>
  );
}
