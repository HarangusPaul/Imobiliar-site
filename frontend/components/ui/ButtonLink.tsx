import type { Route } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import styles from "./ButtonLink.module.css";
import { ArrowRight } from "./icons";

/** A link styled as the design's square, uppercase call-to-action with a trailing arrow. */

export type ButtonVariant = "dark" | "accent";

interface ButtonLinkProps {
  href: Route;
  variant?: ButtonVariant;
  /** Passed to `Link`; false keeps the scroll position, e.g. for "load more". */
  scroll?: boolean;
  children: ReactNode;
}

export function ButtonLink({ href, variant = "dark", scroll, children }: ButtonLinkProps) {
  return (
    <Link href={href} scroll={scroll} className={`${styles.button} ${styles[variant]}`}>
      <span>{children}</span>
      <ArrowRight size={16} className={styles.icon} />
    </Link>
  );
}
