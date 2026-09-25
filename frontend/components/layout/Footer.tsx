import type { Route } from "next";
import Link from "next/link";

import { routes } from "@/lib/constants/routes";

import styles from "./Footer.module.css";

type FooterLink = { label: string; href: Route | `mailto:${string}` | `tel:${string}` };

const GROUPS: Array<{ heading: string; links: FooterLink[] }> = [
  {
    heading: "Explore",
    links: [
      { label: "For Sale", href: routes.buy },
      { label: "Monthly Rent", href: routes.rent },
      { label: "Hotel Experience", href: routes.stay },
      { label: "List a property", href: routes.account.listProperty },
    ],
  },
  {
    heading: "Company",
    links: [
      { label: "Our Story", href: routes.about },
      { label: "Journal", href: routes.about },
      { label: "Careers", href: routes.contact },
    ],
  },
  {
    heading: "Contact",
    links: [
      { label: "London +44 20 7946 0821", href: "tel:+442079460821" },
      { label: "New York +1 212 555 0186", href: "tel:+12125550186" },
      { label: "hello@monument.estate", href: "mailto:hello@monument.estate" },
    ],
  },
];

export function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.content}>
        <div className={styles.brandBlock}>
          <Link href={routes.home} className={styles.brand}>
            MONUMENT®
          </Link>
          <p className={styles.statement}>
            Places of consequence. Selected for architecture, atmosphere and the lives they
            enable.
          </p>
        </div>

        <div className={styles.groups}>
          {GROUPS.map((group) => (
            <div key={group.heading} className={styles.group}>
              <h2 className={styles.heading}>{group.heading}</h2>
              <ul className={styles.list}>
                {group.links.map((link) => (
                  <li key={link.label}>
                    {link.href.startsWith("/") ? (
                      <Link href={link.href as Route} className={styles.link}>
                        {link.label}
                      </Link>
                    ) : (
                      <a href={link.href} className={styles.link}>
                        {link.label}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.legal}>
        <span>© {new Date().getFullYear()} Monument Estate. All rights reserved.</span>
        <span className={styles.policies}>
          <Link href={routes.about}>Privacy</Link>
          <span aria-hidden="true">·</span>
          <Link href={routes.about}>Terms</Link>
          <span aria-hidden="true">·</span>
          <a href="https://instagram.com" rel="noopener noreferrer" target="_blank">
            Instagram
          </a>
        </span>
      </div>
    </footer>
  );
}
