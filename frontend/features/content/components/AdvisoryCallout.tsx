import type { Route } from "next";
import Link from "next/link";

import styles from "./AdvisoryCallout.module.css";

interface AdvisoryCalloutProps {
  title: string;
  text: string;
  action: { label: string; href: Route };
}

function ArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M3.5 8H12.5M12.5 8L8.5 4M12.5 8L8.5 12"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function AdvisoryCallout({ title, text, action }: AdvisoryCalloutProps) {
  return (
    <section className={styles.callout}>
      <span className={styles.glow} aria-hidden="true" />
      <span className={styles.lineTop} aria-hidden="true" />
      <span className={styles.lineBottom} aria-hidden="true" />

      <div className={styles.copy}>
        <h2 className={styles.title}>{title}</h2>
        <p className={styles.text}>{text}</p>
      </div>

      <span className={styles.halo}>
        <span className={styles.ring}>
          <Link href={action.href} className={styles.button}>
            <span className={styles.gloss} aria-hidden="true" />
            <span className={styles.label}>{action.label}</span>
            <span className={styles.iconRing}>
              <span className={styles.icon}>
                <ArrowIcon />
              </span>
            </span>
          </Link>
        </span>
      </span>
    </section>
  );
}
