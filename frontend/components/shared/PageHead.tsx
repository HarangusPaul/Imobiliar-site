import type { ReactNode } from "react";

import styles from "./PageHead.module.css";

/** The dark gradient band under the navbar on form pages (contact, list a property). */
export function PageHead({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className={styles.pageHead}>
      <span className={styles.glow} aria-hidden="true" />
      <div className={styles.copy}>
        <h1 className={styles.title}>{title}</h1>
        <p className={styles.text}>{children}</p>
      </div>
    </div>
  );
}
