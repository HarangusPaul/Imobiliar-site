"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { routes } from "@/lib/constants/routes";

import styles from "./Header.module.css";

/**
 * The section links. A client component only because the active underline
 * depends on the current path.
 */

const NAV_LINKS: Array<{ label: string; href: Route }> = [
  { label: "Buy", href: routes.buy },
  { label: "Rent", href: routes.rent },
  { label: "Stay", href: routes.stay },
  { label: "Journal", href: routes.about },
];

export function NavLinks() {
  const pathname = usePathname();

  return (
    <ul className={styles.links}>
      {NAV_LINKS.map((link) => {
        const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
        return (
          <li key={link.label}>
            <Link
              href={link.href}
              className={`${styles.link} ${active ? styles.active : ""}`}
              aria-current={active ? "page" : undefined}
            >
              {link.label}
              <span className={styles.bar} aria-hidden="true" />
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
